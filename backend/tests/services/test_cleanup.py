from __future__ import annotations

import asyncio
from typing import Any

import pytest

from app import db
from app.services import cleanup, notifier, pdf_service, run_processor
from tests.services.test_run_processor import AUDIENCE, TOPIC, make_fake_llm


@pytest.fixture
def failed_notices(monkeypatch) -> list[tuple[str, str]]:
    calls: list[tuple[str, str]] = []
    monkeypatch.setattr(
        notifier, "notify_run_failed", lambda run_id, code: calls.append((run_id, code))
    )
    return calls


def _age(table: str, row_id: Any, interval: str) -> None:
    with db.connect() as conn:
        conn.execute(
            f"update {table} set created_at = now() - %s::interval where id = %s",
            (interval, row_id),
        )


def test_old_email_requests_are_deleted_and_recent_ones_stay(clean_db):
    run = db.create_run(topic="a", audience="b")
    old = db.create_email_request(run["id"], "regi@example.test")
    recent = db.create_email_request(run["id"], "friss@example.test")
    _age("email_requests", old, "15 days")
    _age("email_requests", recent, "13 days")

    assert cleanup.run_cleanup_once()["deleted_emails"] == 1

    with db.connect() as conn:
        left = conn.execute("select id from email_requests").fetchall()
    assert [row["id"] for row in left] == [recent]


def test_stuck_run_is_failed_and_others_are_untouched(clean_db, failed_notices):
    stuck = db.create_run(topic="a", audience="b")
    fresh = db.create_run(topic="a", audience="b")
    done = db.create_run(topic="a", audience="b")
    sample = db.create_run(topic="a", audience="b")
    db.update_run(stuck["id"], status="running")
    db.update_run(fresh["id"], status="running")
    db.update_run(done["id"], status="completed")
    db.update_run(sample["id"], status="running")
    with db.connect() as conn:
        conn.execute("update runs set is_sample = true where id = %s", (sample["id"],))
    _age("runs", stuck["id"], "11 minutes")
    _age("runs", fresh["id"], "9 minutes")
    _age("runs", done["id"], "11 minutes")
    _age("runs", sample["id"], "11 minutes")

    assert cleanup.run_cleanup_once()["failed_runs"] == 1

    run = db.get_run(stuck["id"])
    assert run["status"] == "failed"
    assert run["completed_at"] is not None
    last = db.list_events(stuck["id"])[-1]
    assert (last["type"], last["error_code"]) == ("run_failed", "RUN_TIMED_OUT")
    assert failed_notices == [(stuck["id"], "RUN_TIMED_OUT")]
    assert db.get_run(fresh["id"])["status"] == "running"
    assert db.get_run(done["id"])["status"] == "completed"
    assert db.get_run(sample["id"])["status"] == "running"
    assert db.list_events(fresh["id"]) == []


async def _fake_pdf(run: dict[str, Any]) -> bytes:
    return b"%PDF-fake"


def test_late_finish_does_not_revive_timed_out_run(clean_db, monkeypatch):
    monkeypatch.setattr(pdf_service, "generate_pdf", _fake_pdf)
    real_synthesis = run_processor.execute_synthesis

    async def synthesis_during_timeout(**kwargs: Any):
        db.fail_stuck_runs(minutes=0)  # a takarító épp most végez a futással
        return await real_synthesis(**kwargs)

    monkeypatch.setattr(run_processor, "execute_synthesis", synthesis_during_timeout)
    finalized: list[bool] = []
    real_finalize = db.finalize_run

    def spying_finalize(run_id: str, **fields: Any) -> bool:
        written = real_finalize(run_id, **fields)
        finalized.append(written)
        return written

    monkeypatch.setattr(db, "finalize_run", spying_finalize)

    row = db.create_run(topic=TOPIC, audience=AUDIENCE)
    asyncio.run(
        run_processor.process_run(
            run_id=row["id"],
            topic=TOPIC,
            audience=AUDIENCE,
            llm_client=make_fake_llm(),
        )
    )

    assert finalized == [False]
    assert db.get_run(row["id"])["status"] == "failed"
    assert db.count_events(row["id"], "run_completed") == 0


def test_cleanup_loop_survives_a_failing_round(monkeypatch, caplog):
    calls: list[int] = []

    def flaky() -> dict[str, int]:
        calls.append(1)
        if len(calls) == 1:
            raise RuntimeError("nyers")
        return {"deleted_emails": 0, "failed_runs": 0}

    monkeypatch.setattr(cleanup, "run_cleanup_once", flaky)

    async def scenario() -> None:
        task = asyncio.create_task(cleanup.cleanup_loop(interval_seconds=0))
        for _ in range(200):
            if len(calls) >= 2:
                break
            await asyncio.sleep(0.01)
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task

    with caplog.at_level("INFO", logger="swarmsense.cleanup"):
        asyncio.run(scenario())
    assert len(calls) >= 2
    assert "RuntimeError" in caplog.text
    assert "nyers" not in caplog.text
