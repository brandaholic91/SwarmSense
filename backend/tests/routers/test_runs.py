from __future__ import annotations

import uuid

import pytest
from fastapi.testclient import TestClient

from app import db
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

    with TestClient(create_app()) as test_client:
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
        {},
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
    r = client.post("/api/v1/runs/", json={"topic": "a", "audience": "b"})
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


def test_get_status_returns_progress(client):
    row = db.create_run(topic="a", audience="b")
    db.update_run(row["id"], status="running", persona_count=7)
    body = client.get(f"/api/v1/runs/{row['id']}/status").json()
    assert body == {
        "run_id": row["id"],
        "status": "running",
        "persona_count": 7,
        "total_personas": 18,
        "updated_at": body["updated_at"],
    }
    assert body["updated_at"] is not None


@pytest.mark.parametrize("run_id", [str(uuid.uuid4()), "abc", "x" * 200])
def test_get_status_unknown_or_malformed_id_is_404(client, run_id):
    r = client.get(f"/api/v1/runs/{run_id}/status")
    assert r.status_code == 404
    assert r.json()["code"] == "RUN_NOT_FOUND"


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


def test_cors_allows_frontend_origin(client):
    r = client.get("/", headers={"Origin": "http://localhost:3000"})
    assert r.headers.get("access-control-allow-origin") == "http://localhost:3000"


def test_cors_blocks_unknown_origin(client):
    r = client.get("/", headers={"Origin": "https://evil.example.com"})
    assert "access-control-allow-origin" not in r.headers
