from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

import pytest
from fastapi.testclient import TestClient

from app import db
from app.core import pricing
from app.core.config import get_settings
from app.core.errors import ErrorCode
from app.routers import runs as runs_router
from app.services import limits

HEADERS = {"X-Internal-Secret": "test-internal-secret"}


@pytest.fixture
def dispatched(monkeypatch) -> list[dict]:
    calls: list[dict] = []
    monkeypatch.setattr(
        runs_router, "dispatch_run_processing", lambda **kwargs: calls.append(kwargs)
    )
    return calls


@pytest.fixture
def client(clean_db, dispatched):
    from app.main import create_app

    with TestClient(create_app(), headers=HEADERS) as test_client:
        yield test_client


def _run_count() -> int:
    with db.connect() as conn:
        return conn.execute("select count(*) as n from runs").fetchone()["n"]


def test_create_run_inserts_row_and_dispatches(client, dispatched):
    r = client.post(
        "/api/v1/runs",
        json={"topic": "  Árazás ", "audience": "KKV vezetők"},
        headers=HEADERS,
    )
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "queued"
    assert db.get_run(body["run_id"])["topic"] == "Árazás"
    assert dispatched == [
        {"run_id": body["run_id"], "topic": "Árazás", "audience": "KKV vezetők"}
    ]


def test_create_run_stores_hashed_client_ip(client):
    r = client.post(
        "/api/v1/runs",
        json={"topic": "a", "audience": "b"},
        headers={**HEADERS, "X-Client-IP": "203.0.113.7"},
    )
    assert r.status_code == 200
    with db.connect() as conn:
        row = conn.execute("select * from runs").fetchone()
    assert row["ip_hash"] == limits.hash_ip("203.0.113.7")
    assert all("203.0.113.7" not in str(value) for value in row.values())


def test_create_run_without_client_ip_header_has_no_hash(client):
    client.post("/api/v1/runs", json={"topic": "a", "audience": "b"}, headers=HEADERS)
    with db.connect() as conn:
        assert conn.execute("select ip_hash from runs").fetchone()["ip_hash"] is None


@pytest.mark.parametrize(
    "code", [ErrorCode.BUSY, ErrorCode.IP_LIMIT_REACHED, ErrorCode.DAILY_LIMIT_REACHED]
)
def test_create_run_full_limit_is_429(client, dispatched, monkeypatch, code):
    monkeypatch.setattr(limits, "check_run_limits", lambda ip_hash: code)
    r = client.post(
        "/api/v1/runs", json={"topic": "a", "audience": "b"}, headers=HEADERS
    )
    assert r.status_code == 429
    assert r.json()["code"] == code.value
    assert _run_count() == 0
    assert dispatched == []


@pytest.mark.parametrize(
    "headers",
    [
        {"X-Internal-Secret": ""},
        {"X-Internal-Secret": "rossz"},
        {"X-Internal-Secret": "titok-é".encode("utf-8")},  # nem-ASCII érték
    ],
)
def test_create_run_without_valid_secret_is_401(client, dispatched, headers):
    r = client.post(
        "/api/v1/runs", json={"topic": "a", "audience": "b"}, headers=headers
    )
    assert r.status_code == 401
    assert r.json()["code"] == "UNAUTHORIZED"
    assert _run_count() == 0
    assert dispatched == []


def test_trailing_slash_still_requires_secret(client, dispatched):
    r = client.post(
        "/api/v1/runs/",
        json={"topic": "a", "audience": "b"},
        headers={"X-Internal-Secret": ""},
    )
    assert r.status_code == 401
    assert dispatched == []


@pytest.mark.parametrize(
    "payload",
    [
        {"topic": "", "audience": "a"},
        {"topic": "   ", "audience": "a"},
        {"topic": "a", "audience": ""},
        {"topic": "x" * 501, "audience": "a"},
        {"topic": "a", "audience": "x" * 501},
        {"topic": "a"},
        {"topic": "a", "audience": "b", "user_id": "u1"},
    ],
)
def test_create_run_invalid_payload_is_422(client, dispatched, payload):
    r = client.post("/api/v1/runs", json=payload, headers=HEADERS)
    assert r.status_code == 422
    assert _run_count() == 0
    assert dispatched == []


def test_create_run_accepts_exactly_500_chars(client, dispatched):
    r = client.post(
        "/api/v1/runs",
        json={"topic": "x" * 500, "audience": "y" * 500},
        headers=HEADERS,
    )
    assert r.status_code == 200


def test_create_run_db_failure_returns_code_and_does_not_dispatch(
    client, dispatched, monkeypatch, caplog
):
    def boom(**_):
        raise RuntimeError("connection refused: postgres://user:titok@host")

    monkeypatch.setattr(db, "create_run", boom)
    r = client.post(
        "/api/v1/runs", json={"topic": "a", "audience": "b"}, headers=HEADERS
    )
    assert r.status_code == 500
    assert r.json()["code"] == "RUN_START_FAILED"
    assert "titok" not in r.text
    assert dispatched == []
    # a napló sem tartalmazhat kivételszöveget vagy tracebacket
    assert "run creation failed: RuntimeError" in caplog.text
    assert "titok" not in caplog.text
    assert "Traceback" not in caplog.text


def test_create_run_limit_check_db_failure_is_500(client, dispatched, monkeypatch):
    def boom(_):
        raise RuntimeError("connection refused")

    monkeypatch.setattr(limits, "check_run_limits", boom)
    r = client.post(
        "/api/v1/runs", json={"topic": "a", "audience": "b"}, headers=HEADERS
    )
    assert r.status_code == 500
    assert r.json()["code"] == "RUN_START_FAILED"
    assert dispatched == []


def test_startup_applies_schema_on_empty_database(clean_db):
    from app.main import create_app

    try:
        with db.connect() as conn:
            conn.execute("drop table email_requests, run_events, runs")
        with TestClient(create_app()):
            pass
        assert db.create_run(topic="a", audience="b")["status"] == "queued"
    finally:
        db.apply_schema()


def test_non_run_endpoints_not_blocked(client):
    r = client.get("/api/v1/status")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_docs_disabled_in_production(monkeypatch):
    from app.main import create_app

    monkeypatch.setenv("SWARMSENSE_ENVIRONMENT", "production")
    get_settings.cache_clear()
    client = TestClient(create_app(), raise_server_exceptions=False)
    assert client.get("/docs").status_code == 404
    assert client.get("/redoc").status_code == 404


def test_no_cors_headers(client):
    r = client.get("/", headers={"Origin": "http://localhost:3000"})
    assert "access-control-allow-origin" not in r.headers


def _make_run_with_events():
    row = db.create_run(topic="Árazás", audience="b")
    db.update_run(row["id"], status="running")
    first = db.insert_event(row["id"], "run_started")
    second = db.insert_event(
        row["id"],
        "persona_retry",
        persona_index=7,
        persona_name="Kovács Anna",
        attempt=2,
        error_code="RATE_LIMITED",
    )
    return row, first, second


def test_events_returns_status_topic_price_and_events(client):
    row, first, second = _make_run_with_events()
    body = client.get(f"/api/v1/runs/{row['id']}/events").json()
    assert set(body) == {"status", "is_sample", "topic", "created_at", "price", "events"}
    assert body["status"] == "running"
    assert body["is_sample"] is False
    assert body["topic"] == "Árazás"
    assert body["price"] == pricing.price_payload()
    assert [e["id"] for e in body["events"]] == [first, second]
    assert "persona_index" not in body["events"][0]
    assert body["events"][0]["type"] == "run_started"
    assert body["events"][0]["at"]
    assert body["events"][1]["persona_name"] == "Kovács Anna"
    assert body["events"][1]["error_code"] == "RATE_LIMITED"


def test_events_after_cursor_returns_only_newer(client):
    row, first, second = _make_run_with_events()
    body = client.get(f"/api/v1/runs/{row['id']}/events?after={first}").json()
    assert [e["id"] for e in body["events"]] == [second]


@pytest.mark.parametrize("run_id", [str(uuid.uuid4()), "abc"])
def test_events_unknown_or_malformed_id_is_404(client, run_id):
    r = client.get(f"/api/v1/runs/{run_id}/events")
    assert r.status_code == 404
    assert r.json()["code"] == "RUN_NOT_FOUND"


@pytest.mark.parametrize("after", ["-1", "x"])
def test_events_invalid_after_is_422(client, after):
    row = db.create_run(topic="a", audience="b")
    r = client.get(f"/api/v1/runs/{row['id']}/events?after={after}")
    assert r.status_code == 422


def test_events_db_failure_is_503_with_code(client, monkeypatch, caplog):
    def boom(_):
        raise RuntimeError("connection refused: postgres://user:titok@host")

    monkeypatch.setattr(db, "get_run", boom)
    r = client.get(f"/api/v1/runs/{uuid.uuid4()}/events")
    assert r.status_code == 503
    assert r.json()["code"] == "SERVICE_UNAVAILABLE"
    assert "titok" not in r.text
    assert "RuntimeError" in caplog.text
    assert "titok" not in caplog.text
    assert "Traceback" not in caplog.text


def test_get_run_returns_detail(client):
    row = db.create_run(topic="Árazás", audience="KKV")
    db.insert_event(row["id"], "persona_retry", persona_index=1, attempt=2)
    db.insert_event(row["id"], "persona_retry", persona_index=2, attempt=2)
    db.insert_event(row["id"], "run_started")
    result = {"stance_counts": {"support": 1}, "synthesis": None, "failed_personas": []}
    created_at = db.get_run(row["id"])["created_at"]
    completed_at = created_at + timedelta(milliseconds=86500)
    db.update_run(
        row["id"],
        status="partial",
        result=result,
        input_tokens=100,
        output_tokens=50,
        completed_at=completed_at,
    )
    r = client.get(f"/api/v1/runs/{row['id']}")
    assert r.status_code == 200
    body = r.json()
    assert set(body) == {
        "run_id", "status", "is_sample", "topic", "audience", "created_at",
        "completed_at", "duration_ms", "input_tokens", "output_tokens",
        "retry_count", "price", "result",
    }
    assert body["run_id"] == row["id"]
    assert body["status"] == "partial"
    assert body["retry_count"] == 2
    assert body["duration_ms"] == 86500
    assert body["result"] == result
    assert (body["input_tokens"], body["output_tokens"]) == (100, 50)
    assert body["price"] == pricing.price_payload()
    assert "ip_hash" not in r.text and "pdf" not in body


def test_get_run_running_has_null_result_and_duration(client):
    row = db.create_run(topic="a", audience="b")
    db.update_run(row["id"], status="running")
    body = client.get(f"/api/v1/runs/{row['id']}").json()
    assert body["status"] == "running"
    assert body["result"] is None
    assert body["duration_ms"] is None
    assert body["completed_at"] is None


def test_get_run_failed_has_null_result(client):
    row = db.create_run(topic="a", audience="b")
    db.update_run(
        row["id"], status="failed", result={"x": 1}, completed_at=datetime.now(UTC)
    )
    assert client.get(f"/api/v1/runs/{row['id']}").json()["result"] is None


@pytest.mark.parametrize("run_id", [str(uuid.uuid4()), "abc"])
def test_get_run_unknown_is_404(client, run_id):
    r = client.get(f"/api/v1/runs/{run_id}")
    assert r.status_code == 404
    assert r.json()["code"] == "RUN_NOT_FOUND"


def test_get_run_requires_secret(client):
    row = db.create_run(topic="a", audience="b")
    r = client.get(f"/api/v1/runs/{row['id']}", headers={"X-Internal-Secret": ""})
    assert r.status_code == 401


def test_get_run_db_failure_is_503_with_code(client, monkeypatch):
    def boom(_):
        raise RuntimeError("postgres://user:titok@host")

    monkeypatch.setattr(db, "get_run", boom)
    r = client.get(f"/api/v1/runs/{uuid.uuid4()}")
    assert r.status_code == 503
    assert r.json()["code"] == "SERVICE_UNAVAILABLE"
    assert "titok" not in r.text


def test_every_runs_endpoint_requires_secret(client):
    run_id = uuid.uuid4()
    no_secret = {"X-Internal-Secret": ""}
    assert (
        client.post(
            "/api/v1/runs", json={"topic": "a", "audience": "b"}, headers=no_secret
        ).status_code
        == 401
    )
    for path in (f"/api/v1/runs/{run_id}/events", f"/api/v1/runs/{run_id}/events/"):
        assert client.get(path, headers=no_secret).status_code == 401


def test_status_and_root_are_open(client):
    no_secret = {"X-Internal-Secret": ""}
    assert client.get("/", headers=no_secret).status_code == 200
    assert client.get("/api/v1/status", headers=no_secret).status_code == 200
