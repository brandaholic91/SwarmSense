import uuid
from datetime import UTC, datetime

import pytest

from app import db


def test_create_run_inserts_queued_row(clean_db):
    row = db.create_run(topic="Árazás", audience="KKV vezetők")
    assert uuid.UUID(row["id"])
    assert row["status"] == "queued"
    assert row["created_at"].tzinfo is not None


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


def test_update_run_rejects_unknown_column(clean_db):
    created = db.create_run(topic="Árazás", audience="KKV vezetők")
    with pytest.raises(ValueError):
        db.update_run(created["id"], topic="más")


def test_update_run_rejects_invalid_status(clean_db):
    created = db.create_run(topic="Árazás", audience="KKV vezetők")
    with pytest.raises(Exception):
        db.update_run(created["id"], status="nonsense")
    assert db.get_run(created["id"])["status"] == "queued"


def test_apply_schema_is_idempotent(clean_db):
    db.apply_schema()
    db.apply_schema()
    assert db.create_run(topic="a", audience="b")["status"] == "queued"
