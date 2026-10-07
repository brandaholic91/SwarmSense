from __future__ import annotations

import runpy
import sys
from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient

from app import db

RESULT = {"completed_persona_count": 1, "synthesis": {"summary": "Összefoglaló ő"}}


def _make_recorded_run(topic: str = "Árazás") -> str:
    """Egy futás eredménnyel, PDF-fel, ip_hash-sel és 5 eseménnyel (retry és failed is)."""
    run = db.create_run(topic=topic, audience="KKV vezetők", ip_hash="secret-hash")
    run_id = run["id"]
    db.update_run(
        run_id,
        status="completed",
        persona_count=18,
        support_count=3,
        reject_count=1,
        conditional_count=2,
        synthesis_summary="Röviden",
        synthesis_main_barriers=["ár", "bizalom"],
        input_tokens=11,
        output_tokens=22,
        completed_at=datetime(2026, 10, 7, 12, 0, 9, tzinfo=UTC),
        result=RESULT,
    )
    db.save_pdf(run_id, b"%PDF-secret")
    db.insert_event(run_id, "run_started")
    db.insert_event(run_id, "persona_started", persona_index=0, persona_name="Anna")
    db.insert_event(run_id, "persona_retry", persona_index=0, attempt=2, error_code="LLM_TIMEOUT")
    db.insert_event(
        run_id,
        "persona_failed",
        persona_index=0,
        attempt=3,
        error_code="X",
        duration_ms=1200,
        input_tokens=5,
        output_tokens=6,
    )
    db.insert_event(run_id, "run_completed")
    # különböző, ismert időbélyegek
    with db.connect() as conn:
        for i, event in enumerate(db.list_events(run_id)):
            conn.execute(
                "update run_events set created_at = %s where id = %s",
                (datetime(2026, 10, 7, 12, 0, i, 123456, tzinfo=UTC), event["id"]),
            )
    return run_id


def _truncate() -> None:
    with db.connect() as conn:
        conn.execute("truncate runs, run_events restart identity cascade")


def _snapshot(run_id: str):
    return [(e["type"], e["created_at"]) for e in db.list_events(run_id)]


def _write_seed(tmp_path, run_id: str):
    seed = tmp_path / "sample_run.sql"
    seed.write_text(db.export_sample_sql(run_id), encoding="utf-8")
    return seed


def test_export_then_seed_roundtrip(clean_db):
    run_id = _make_recorded_run()
    original = db.get_run(run_id)
    original_events = _snapshot(run_id)

    sql_text = db.export_sample_sql(run_id)
    assert "secret-hash" not in sql_text
    assert "PDF-secret" not in sql_text

    _truncate()
    with db.connect() as conn:
        conn.execute(sql_text)

    restored = db.get_run(run_id)
    assert restored["is_sample"] is True and restored["ip_hash"] is None
    assert restored["result"] == original["result"]
    assert restored["created_at"] == original["created_at"]
    assert restored["completed_at"] == original["completed_at"]
    assert restored["synthesis_main_barriers"] == ["ár", "bizalom"]
    assert restored["topic"] == original["topic"]
    assert db.get_pdf(run_id) is None
    assert _snapshot(run_id) == original_events
    assert db.get_sample_run_id() == run_id


def test_export_text_with_quotes_and_accents_roundtrips(clean_db):
    topic = "O'Brien \"ő\" -- ; drop table runs"
    run_id = _make_recorded_run(topic)
    sql_text = db.export_sample_sql(run_id)
    _truncate()
    with db.connect() as conn:
        conn.execute(sql_text)
    assert db.get_run(run_id)["topic"] == topic


def test_export_unknown_run_raises(clean_db):
    with pytest.raises(LookupError):
        db.export_sample_sql("00000000-0000-0000-0000-000000000000")


def test_seed_runs_only_when_no_sample(clean_db, tmp_path, monkeypatch):
    run_id = _make_recorded_run()
    seed = _write_seed(tmp_path, run_id)
    monkeypatch.setattr(db, "SEED_PATH", seed)

    # nincs minta (csak egy közönséges futás): betölt
    _truncate()
    other = db.create_run(topic="más", audience="más")
    assert db.seed_sample_if_missing() is True
    assert db.get_sample_run_id() == run_id
    assert db.get_run(other["id"]) is not None

    # már van minta: nem tölt be
    with db.connect() as conn:
        conn.execute("delete from runs where id = %s", (run_id,))
        conn.execute("update runs set is_sample = true where id = %s", (other["id"],))
    assert db.seed_sample_if_missing() is False
    assert db.get_run(run_id) is None


def test_seed_missing_file_is_noop(clean_db, tmp_path, monkeypatch):
    monkeypatch.setattr(db, "SEED_PATH", tmp_path / "nincs.sql")
    assert db.seed_sample_if_missing() is False
    assert db.get_sample_run_id() is None


def test_seed_is_idempotent(clean_db, tmp_path, monkeypatch):
    run_id = _make_recorded_run()
    monkeypatch.setattr(db, "SEED_PATH", _write_seed(tmp_path, run_id))
    _truncate()
    assert db.seed_sample_if_missing() is True
    assert db.seed_sample_if_missing() is False
    with db.connect() as conn:
        n = conn.execute("select count(*) as n from runs where is_sample").fetchone()["n"]
        events = conn.execute("select count(*) as n from run_events").fetchone()["n"]
    assert n == 1 and events == 5


def test_seed_does_not_touch_existing_run_with_same_id(clean_db):
    # a forrásfutás közönséges (nem minta) sorként már megvan: a seed se eseményt
    # nem fűz hozzá, se mintává nem teszi — akárhányszor fut le
    run_id = _make_recorded_run()
    before = _snapshot(run_id)
    sql_text = db.export_sample_sql(run_id)

    with db.connect() as conn:
        conn.execute(sql_text)
    with db.connect() as conn:
        conn.execute(sql_text)

    assert _snapshot(run_id) == before
    assert db.get_sample_run_id() is None
    with db.connect() as conn:
        assert conn.execute("select count(*) as n from runs").fetchone()["n"] == 1


def test_seed_text_executed_twice_inserts_events_once(clean_db):
    run_id = _make_recorded_run()
    before = _snapshot(run_id)
    sql_text = db.export_sample_sql(run_id)
    _truncate()

    with db.connect() as conn:
        conn.execute(sql_text)
    with db.connect() as conn:
        conn.execute(sql_text)

    assert _snapshot(run_id) == before


def test_export_run_without_events_roundtrips(clean_db):
    run_id = db.create_run(topic="a", audience="b")["id"]
    sql_text = db.export_sample_sql(run_id)
    _truncate()
    with db.connect() as conn:
        conn.execute(sql_text)
    assert db.get_sample_run_id() == run_id
    assert db.list_events(run_id) == []


def test_get_sample_run_id_returns_latest(clean_db):
    first = db.create_run(topic="a", audience="b")["id"]
    second = db.create_run(topic="a", audience="b")["id"]
    with db.connect() as conn:
        conn.execute("update runs set is_sample = true")
        conn.execute(
            "update runs set created_at = now() - interval '1 day' where id = %s", (first,)
        )
    assert db.get_sample_run_id() == second


def test_startup_loads_seed_into_empty_db(clean_db, tmp_path, monkeypatch):
    run_id = _make_recorded_run()
    seed = _write_seed(tmp_path, run_id)
    _truncate()
    monkeypatch.setattr(db, "SEED_PATH", seed)
    from app.main import create_app

    with TestClient(create_app()):
        assert db.get_sample_run_id() == run_id


def test_startup_survives_broken_seed(clean_db, tmp_path, monkeypatch, caplog):
    seed = tmp_path / "sample_run.sql"
    seed.write_text("this is not sql 'secret-text", encoding="utf-8")
    monkeypatch.setattr(db, "SEED_PATH", seed)
    from app.main import create_app

    with TestClient(create_app()) as client:
        assert client.get("/").status_code in (200, 401)
    assert db.get_sample_run_id() is None
    assert "secret-text" not in caplog.text


def _run_script(monkeypatch, tmp_path, run_id: str) -> int | str | None:
    seed = tmp_path / "out" / "sample_run.sql"
    monkeypatch.setattr(db, "SEED_PATH", seed)
    monkeypatch.setattr(sys, "argv", ["export_sample", run_id])
    sys.modules.pop("scripts.export_sample", None)
    with pytest.raises(SystemExit) as exc:
        runpy.run_module("scripts.export_sample", run_name="__main__")
    return exc.value.code


def test_export_script_writes_file_and_prints_summary(clean_db, tmp_path, monkeypatch, capsys):
    run_id = _make_recorded_run()
    assert _run_script(monkeypatch, tmp_path, run_id) in (0, None)
    out = capsys.readouterr().out
    assert "persona_retry: 1" in out and "persona_failed: 1" in out
    written = (tmp_path / "out" / "sample_run.sql").read_text(encoding="utf-8")
    assert written.startswith('with "ins" as (\ninsert into "runs"')


def test_export_script_refuses_run_without_failed_persona(
    clean_db, tmp_path, monkeypatch, capsys
):
    run = db.create_run(topic="a", audience="b")
    db.insert_event(run["id"], "run_started")
    db.insert_event(run["id"], "persona_retry", persona_index=0, attempt=2)
    code = _run_script(monkeypatch, tmp_path, run["id"])
    assert code not in (0, None)
    assert not (tmp_path / "out" / "sample_run.sql").exists()
    assert "persona_failed" in capsys.readouterr().err
