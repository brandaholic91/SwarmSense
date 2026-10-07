import uuid
from datetime import UTC, datetime

import psycopg
import pytest

from app import db


def test_create_run_inserts_queued_row(clean_db):
    row = db.create_run(topic="Árazás", audience="KKV vezetők")
    assert uuid.UUID(row["id"])
    assert row["status"] == "queued"
    assert row["created_at"].tzinfo is not None


def test_create_run_stores_ip_hash(clean_db):
    row = db.create_run(topic="a", audience="b", ip_hash="abc")
    assert db.get_run(row["id"])["ip_hash"] == "abc"


def test_count_active_runs_counts_only_unfinished_non_sample(clean_db):
    queued = db.create_run(topic="a", audience="b")
    running = db.create_run(topic="a", audience="b")
    done = db.create_run(topic="a", audience="b")
    db.update_run(running["id"], status="running")
    db.update_run(done["id"], status="completed")
    assert queued and db.count_active_runs() == 2


def test_count_runs_since_filters_by_hash_and_window(clean_db):
    db.create_run(topic="a", audience="b", ip_hash="x")
    old = db.create_run(topic="a", audience="b", ip_hash="x")
    db.create_run(topic="a", audience="b", ip_hash="y")
    with db.connect() as conn:
        conn.execute(
            "update runs set created_at = now() - interval '25 hours' where id = %s",
            (old["id"],),
        )
    assert db.count_runs_since() == 2
    assert db.count_runs_since(ip_hash="x") == 1
    assert db.count_runs_since(hours=48, ip_hash="x") == 2


def test_get_run_returns_row_without_pdf(clean_db):
    created = db.create_run(topic="Árazás", audience="KKV vezetők")
    row = db.get_run(created["id"])
    assert row["id"] == created["id"]
    assert row["topic"] == "Árazás"
    assert row["persona_count"] == 0
    assert row["input_tokens"] == 0
    assert "pdf" not in row


def test_get_run_missing_returns_none(clean_db):
    assert db.get_run(str(uuid.uuid4())) is None


@pytest.mark.parametrize("bad_id", ["abc", "", "123", "'; drop table runs; --"])
def test_get_run_invalid_uuid_returns_none(clean_db, bad_id):
    assert db.get_run(bad_id) is None


def test_update_run_writes_listed_columns(clean_db):
    created = db.create_run(topic="Árazás", audience="KKV vezetők")
    now = datetime.now(UTC)
    db.update_run(
        created["id"],
        status="completed",
        persona_count=18,
        synthesis_main_barriers=["ár", "bizalom"],
        input_tokens=100,
        output_tokens=50,
        completed_at=now,
    )
    row = db.get_run(created["id"])
    assert row["status"] == "completed"
    assert row["persona_count"] == 18
    assert row["synthesis_main_barriers"] == ["ár", "bizalom"]
    assert (row["input_tokens"], row["output_tokens"]) == (100, 50)
    assert row["completed_at"] == now


def test_update_run_stores_json_result(clean_db):
    created = db.create_run(topic="t", audience="a")
    db.update_run(created["id"], result={"á": [1, 2]})
    assert db.get_run(created["id"])["result"] == {"á": [1, 2]}


def test_count_events_counts_by_type(clean_db):
    run = db.create_run(topic="t", audience="a")
    other = db.create_run(topic="t", audience="a")
    db.insert_event(run["id"], "persona_retry")
    db.insert_event(run["id"], "persona_retry")
    db.insert_event(run["id"], "run_started")
    db.insert_event(other["id"], "persona_retry")
    assert db.count_events(run["id"], "persona_retry") == 2
    assert db.count_events(run["id"], "run_failed") == 0
    assert db.count_events("nem-uuid", "persona_retry") == 0


def test_update_run_rejects_unknown_column(clean_db):
    created = db.create_run(topic="Árazás", audience="KKV vezetők")
    with pytest.raises(ValueError):
        db.update_run(created["id"], topic="más")


def test_update_run_rejects_invalid_status(clean_db):
    created = db.create_run(topic="Árazás", audience="KKV vezetők")
    with pytest.raises(psycopg.errors.CheckViolation):
        db.update_run(created["id"], status="nonsense")
    assert db.get_run(created["id"])["status"] == "queued"


def test_insert_and_list_events_in_order(clean_db):
    run = db.create_run(topic="t", audience="a")
    first = db.insert_event(run["id"], "run_started")
    second = db.insert_event(
        run["id"], "persona_retry", persona_index=7, persona_name="Kovács Anna",
        attempt=2, error_code="RATE_LIMITED",
    )
    events = db.list_events(run["id"])
    assert [e["id"] for e in events] == [first, second]
    assert events[1]["attempt"] == 2 and events[1]["persona_name"] == "Kovács Anna"
    assert [e["id"] for e in db.list_events(run["id"], after=first)] == [second]


def test_insert_event_rejects_unknown_field(clean_db):
    run = db.create_run(topic="t", audience="a")
    with pytest.raises(ValueError):
        db.insert_event(run["id"], "run_started", error_message="nyers szöveg")


def test_list_events_invalid_run_id_is_empty(clean_db):
    assert db.list_events("nem-uuid") == []


def test_apply_schema_is_idempotent(clean_db):
    db.apply_schema()
    db.apply_schema()
    assert db.create_run(topic="a", audience="b")["status"] == "queued"


def test_email_requests_are_counted_per_run_and_window(clean_db):
    first = db.create_run(topic="a", audience="b")["id"]
    second = db.create_run(topic="a", audience="b")["id"]
    request_id = db.create_email_request(first, "reader@example.com")
    db.create_email_request(first, "reader@example.com")
    old_id = db.create_email_request(second, "reader@example.com")
    with db.connect() as conn:
        conn.execute(
            "update email_requests set created_at = now() - interval '25 hours' "
            "where id = %s",
            (old_id,),
        )
    assert db.count_email_requests(run_id=first) == 2
    assert db.count_email_requests(run_id=second) == 1
    assert db.count_email_requests(hours=24) == 2
    assert db.count_email_requests() == 3
    assert db.count_email_requests(run_id="not-a-uuid") == 0

    db.mark_email_sent(request_id)
    with db.connect() as conn:
        sent = conn.execute(
            "select sent_at from email_requests where id = %s", (request_id,)
        ).fetchone()["sent_at"]
    assert sent is not None
