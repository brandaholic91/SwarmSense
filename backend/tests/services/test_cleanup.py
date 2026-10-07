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


def test_old_ip_hashes_are_cleared_and_recent_ones_stay(clean_db):
    old = db.create_run(topic="a", audience="b", ip_hash="regi")
    recent = db.create_run(topic="a", audience="b", ip_hash="friss")
    _age("runs", old["id"], "25 hours")
    _age("runs", recent["id"], "23 hours")

    assert cleanup.run_cleanup_once()["cleared_ip_hashes"] == 1

    assert db.get_run(old["id"])["ip_hash"] is None
    assert db.get_run(recent["id"])["ip_hash"] == "friss"
    # a futás maga megmarad, és a keret a friss futást továbbra is számolja
    assert db.count_runs_since(ip_hash="friss") == 1


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


def _process(llm_client=None) -> str:
    row = db.create_run(topic=TOPIC, audience=AUDIENCE)
    asyncio.run(
        run_processor.process_run(
            run_id=row["id"],
            topic=TOPIC,
            audience=AUDIENCE,
            llm_client=llm_client or make_fake_llm(),
        )
    )
    return row["id"]


def _types(run_id: str) -> list[str]:
    return [e["type"] for e in db.list_events(run_id)]


def _time_out_during(monkeypatch, name: str) -> None:
    """A `run_processor.<name>` hívása előtt a takarító lezárja a futást."""
    real = getattr(run_processor, name)

    async def wrapper(*args: Any, **kwargs: Any):
        db.fail_stuck_runs(minutes=0)
        return await real(*args, **kwargs)

    monkeypatch.setattr(run_processor, name, wrapper)


def test_timeout_during_synthesis_leaves_run_failed(clean_db, monkeypatch):
    monkeypatch.setattr(pdf_service, "generate_pdf", _fake_pdf)
    _time_out_during(monkeypatch, "execute_synthesis")

    run_id = _process()

    run = db.get_run(run_id)
    assert run["status"] == "failed"
    assert run["result"] is None
    assert db.get_pdf(run_id) is None
    assert db.count_events(run_id, "run_completed") == 0


def test_timeout_between_result_and_final_status_does_not_revive_run(
    clean_db, monkeypatch
):
    async def timing_out_pdf(run: dict[str, Any]) -> bytes:
        db.fail_stuck_runs(minutes=0)
        return b"%PDF-fake"

    monkeypatch.setattr(pdf_service, "generate_pdf", timing_out_pdf)
    finalized: list[bool] = []
    real_finalize = db.finalize_run

    def spying_finalize(run_id: str, **fields: Any) -> bool:
        written = real_finalize(run_id, **fields)
        finalized.append(written)
        return written

    monkeypatch.setattr(db, "finalize_run", spying_finalize)

    run_id = _process()

    assert finalized == [False]
    assert db.get_run(run_id)["status"] == "failed"
    assert db.count_events(run_id, "run_completed") == 0


def test_timeout_during_persona_engine_leaves_run_failed(
    clean_db, monkeypatch, failed_notices
):
    monkeypatch.setattr(pdf_service, "generate_pdf", _fake_pdf)
    _time_out_during(monkeypatch, "execute_persona_engine")
    row = db.create_run(topic=TOPIC, audience=AUDIENCE)
    asyncio.run(
        run_processor.process_run(
            run_id=row["id"], topic=TOPIC, audience=AUDIENCE, llm_client=make_fake_llm()
        )
    )
    # a takarító dolgát a run_cleanup_once végzi: itt a processzor viselkedése számít
    assert db.get_run(row["id"])["status"] == "failed"
    types = _types(row["id"])
    assert "run_completed" not in types
    assert "synthesis_started" not in types
    assert failed_notices == []


def test_cleanup_then_processor_gives_exactly_one_failure_event_and_notice(
    clean_db, monkeypatch, failed_notices
):
    row = db.create_run(topic=TOPIC, audience=AUDIENCE)
    real_engine = run_processor.execute_persona_engine

    async def engine_after_cleanup(**kwargs: Any):
        cleanup.run_cleanup_once()  # a takarító előbb végez
        return await real_engine(**kwargs)

    monkeypatch.setattr(run_processor, "execute_persona_engine", engine_after_cleanup)
    # a takarítónak 0 perces küszöb kell: a futás épp most indult
    real_fail_stuck = db.fail_stuck_runs
    monkeypatch.setattr(
        db, "fail_stuck_runs", lambda **kw: real_fail_stuck(minutes=0)
    )
    asyncio.run(
        run_processor.process_run(
            run_id=row["id"],
            topic=TOPIC,
            audience=AUDIENCE,
            llm_client=make_fake_llm(blueprint_fails=True),
        )
    )

    completed_at = db.get_run(row["id"])["completed_at"]
    assert db.get_run(row["id"])["status"] == "failed"
    assert _types(row["id"]).count("run_failed") == 1
    assert failed_notices == [(row["id"], "RUN_TIMED_OUT")]
    # a processzor saját bukása nem írta felül a `completed_at`-et
    assert completed_at is not None


def test_processor_failure_after_cleanup_keeps_completed_at(
    clean_db, monkeypatch, failed_notices
):
    row = db.create_run(topic=TOPIC, audience=AUDIENCE)
    seen: dict[str, Any] = {}
    real_engine = run_processor.execute_persona_engine

    async def engine_after_timeout(**kwargs: Any):
        db.fail_stuck_runs(minutes=0)
        seen["completed_at"] = db.get_run(row["id"])["completed_at"]
        return await real_engine(**kwargs)

    monkeypatch.setattr(run_processor, "execute_persona_engine", engine_after_timeout)
    asyncio.run(
        run_processor.process_run(
            run_id=row["id"],
            topic=TOPIC,
            audience=AUDIENCE,
            llm_client=make_fake_llm(blueprint_fails=True),
        )
    )

    assert db.get_run(row["id"])["completed_at"] == seen["completed_at"]
    assert "run_failed" not in _types(row["id"])
    assert failed_notices == []


def test_run_failed_while_queued_is_not_started(clean_db, failed_notices):
    row = db.create_run(topic=TOPIC, audience=AUDIENCE)
    db.fail_stuck_runs(minutes=0)

    result = asyncio.run(
        run_processor.process_run(
            run_id=row["id"], topic=TOPIC, audience=AUDIENCE, llm_client=make_fake_llm()
        )
    )

    assert result is None
    assert db.get_run(row["id"])["status"] == "failed"
    assert db.list_events(row["id"]) == []
    assert failed_notices == []


def test_one_failing_run_does_not_skip_the_others(
    clean_db, monkeypatch, failed_notices
):
    first = db.create_run(topic="a", audience="b")
    second = db.create_run(topic="a", audience="b")
    for run in (first, second):
        db.update_run(run["id"], status="running")
        _age("runs", run["id"], "11 minutes")
    real_insert = db.insert_event

    def flaky_insert(run_id: str, type: str, **fields: Any) -> int:
        if run_id == first["id"]:
            raise RuntimeError("nyers")
        return real_insert(run_id, type, **fields)

    monkeypatch.setattr(db, "insert_event", flaky_insert)
    monkeypatch.setattr(
        db, "fail_stuck_runs", lambda **kw: [first["id"], second["id"]]
    )

    cleanup.run_cleanup_once()

    assert _types(second["id"]) == ["run_failed"]
    assert (second["id"], "RUN_TIMED_OUT") in failed_notices


async def _run_loop_for(seconds: float, **kwargs: Any) -> None:
    task = asyncio.create_task(cleanup.cleanup_loop(**kwargs))
    await asyncio.sleep(seconds)
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task


def test_stuck_sweep_runs_often_and_email_deletion_rarely(monkeypatch):
    stuck: list[int] = []
    emails: list[int] = []
    monkeypatch.setattr(cleanup, "fail_stuck_runs_once", lambda: stuck.append(1) or 0)
    monkeypatch.setattr(cleanup, "delete_old_emails_once", lambda: emails.append(1) or 0)
    monkeypatch.setattr(cleanup, "clear_old_ip_hashes_once", lambda: 0)

    asyncio.run(
        _run_loop_for(0.3, interval_seconds=3600, stuck_interval_seconds=0.02)
    )

    assert len(stuck) >= 3
    assert emails == [1]


def test_failing_stuck_sweep_does_not_stop_email_deletion(monkeypatch, caplog):
    emails: list[int] = []

    def broken() -> int:
        raise RuntimeError("nyers")

    monkeypatch.setattr(cleanup, "fail_stuck_runs_once", broken)
    monkeypatch.setattr(cleanup, "clear_old_ip_hashes_once", lambda: 0)
    monkeypatch.setattr(cleanup, "delete_old_emails_once", lambda: emails.append(1) or 0)

    with caplog.at_level("INFO", logger="swarmsense.cleanup"):
        asyncio.run(
            _run_loop_for(0.3, interval_seconds=0.02, stuck_interval_seconds=0.02)
        )

    assert len(emails) >= 3
    assert "RuntimeError" in caplog.text
    assert "nyers" not in caplog.text


def test_failing_email_deletion_does_not_stop_stuck_sweep(monkeypatch, caplog):
    stuck: list[int] = []

    def broken() -> int:
        raise RuntimeError("nyers")

    monkeypatch.setattr(cleanup, "fail_stuck_runs_once", lambda: stuck.append(1) or 0)
    monkeypatch.setattr(cleanup, "delete_old_emails_once", broken)
    monkeypatch.setattr(cleanup, "clear_old_ip_hashes_once", lambda: 0)

    with caplog.at_level("INFO", logger="swarmsense.cleanup"):
        asyncio.run(
            _run_loop_for(0.3, interval_seconds=0.02, stuck_interval_seconds=0.02)
        )

    assert len(stuck) >= 3
    assert "RuntimeError" in caplog.text
    assert "nyers" not in caplog.text
