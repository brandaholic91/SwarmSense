from __future__ import annotations

import importlib
from datetime import UTC, datetime

from fastapi.testclient import TestClient

from app.core import cost_enforcement
from app.core.config import get_settings
from app.core.database import get_supabase_client

TEST_INTERNAL_SECRET = "test-internal-secret"
INTERNAL_SECRET_HEADER = {"X-Internal-Secret": TEST_INTERNAL_SECRET}

VALID_PAYLOAD = {
    "user_id": "user-1",
    "topic": "Pricing",
    "audience": "SMB CFO",
    "role_answer": "founder_ceo",
    "use_case_answer": "message_validation",
}


class FakeResponse:
    def __init__(self, data):
        self.data = data


class FakeQuery:
    def __init__(self, supabase, table_name: str):
        self._supabase = supabase
        self._table_name = table_name
        self._payload: dict[str, object] | None = None
        self._operation = "select"

    def select(self, _fields: str):
        self._operation = "select"
        return self

    def eq(self, _field: str, _value: object):
        return self

    def limit(self, _n: int):
        return self

    def insert(self, payload: dict[str, object]):
        self._operation = "insert"
        self._payload = payload
        return self

    def execute(self):
        if self._table_name == "cost_tracking" and self._operation == "select":
            return FakeResponse(self._supabase.cost_rows)

        if self._table_name == "runs" and self._operation == "insert":
            assert self._payload is not None
            run_id = f"run-{len(self._supabase.inserted_runs) + 1}"
            row = {
                "id": run_id,
                "user_id": self._payload["user_id"],
                "topic": self._payload["topic"],
                "audience": self._payload["audience"],
                "status": self._payload["status"],
                "created_at": datetime.now(UTC).isoformat(),
            }
            self._supabase.inserted_runs.append(row)
            return FakeResponse([row])

        if self._table_name == "qualifier_responses" and self._operation == "insert":
            assert self._payload is not None
            qualifier_id = f"qualifier-{len(self._supabase.inserted_qualifiers) + 1}"
            row = {
                "id": qualifier_id,
                "run_id": self._payload["run_id"],
                "user_id": self._payload["user_id"],
                "role_answer": self._payload["role_answer"],
                "use_case_answer": self._payload["use_case_answer"],
                "created_at": datetime.now(UTC).isoformat(),
            }
            self._supabase.inserted_qualifiers.append(row)
            return FakeResponse([row])

        return FakeResponse([])


class FakeSupabase:
    def __init__(self, total_usd: str | None):
        self.cost_rows = [] if total_usd is None else [{"total_usd": total_usd}]
        self.inserted_runs: list[dict[str, object]] = []
        self.inserted_qualifiers: list[dict[str, object]] = []

    def table(self, name: str):
        return FakeQuery(self, name)


def build_client(monkeypatch, fake_supabase: FakeSupabase) -> TestClient:
    monkeypatch.setenv("SWARMSENSE_SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setenv("SWARMSENSE_SUPABASE_SERVICE_KEY", "service-key")
    monkeypatch.setenv("SWARMSENSE_KIMI_API_KEY", "kimi-key")
    monkeypatch.setenv("SWARMSENSE_OPENROUTER_API_KEY", "or_test")
    monkeypatch.setenv("SWARMSENSE_OPERATOR_API_KEY", "operator-key")
    monkeypatch.setenv("SWARMSENSE_INTERNAL_SECRET", TEST_INTERNAL_SECRET)
    monkeypatch.setenv("SWARMSENSE_ENVIRONMENT", "development")
    monkeypatch.setenv("SWARMSENSE_BACKEND_ORIGIN", "https://api.swarmsense.ai")
    monkeypatch.setenv("SWARMSENSE_FRONTEND_ORIGIN", "https://swarmsense.vercel.app")
    monkeypatch.setenv("SWARMSENSE_RESEND_API_KEY", "re_test")

    get_settings.cache_clear()
    get_supabase_client.cache_clear()
    import app.main as main
    import app.routers.run_sessions as run_sessions_router

    importlib.reload(run_sessions_router)
    importlib.reload(main)

    monkeypatch.setattr(cost_enforcement, "get_supabase_client", lambda: fake_supabase)
    monkeypatch.setattr(run_sessions_router, "get_supabase_client", lambda: fake_supabase)

    return TestClient(main.app)


def test_run_session_creates_run_and_qualifier(monkeypatch):
    fake_supabase = FakeSupabase("1.00")
    client = build_client(monkeypatch, fake_supabase)

    response = client.post(
        "/api/v1/run-sessions",
        json=VALID_PAYLOAD,
        headers=INTERNAL_SECRET_HEADER,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "queued"
    assert body["run_id"] == "run-1"
    assert isinstance(body["created_at"], str)
    assert len(fake_supabase.inserted_runs) == 1
    assert len(fake_supabase.inserted_qualifiers) == 1
    assert fake_supabase.inserted_qualifiers[0]["run_id"] == "run-1"
    assert fake_supabase.inserted_qualifiers[0]["user_id"] == "user-1"


def test_run_session_dispatches_background_task(monkeypatch):
    fake_supabase = FakeSupabase("1.00")
    client = build_client(monkeypatch, fake_supabase)

    import app.routers.run_sessions as run_sessions_router

    captured: list[dict[str, str]] = []

    def fake_dispatch(*, run_id: str, user_id: str, topic: str, audience: str) -> None:
        captured.append({"run_id": run_id, "user_id": user_id, "topic": topic, "audience": audience})

    monkeypatch.setattr(run_sessions_router, "dispatch_run_processing", fake_dispatch)

    client.post(
        "/api/v1/run-sessions",
        json=VALID_PAYLOAD,
        headers=INTERNAL_SECRET_HEADER,
    )

    assert captured == [{"run_id": "run-1", "user_id": "user-1", "topic": "Pricing", "audience": "SMB CFO"}]


def test_run_session_blocked_at_cap_and_no_rows_created(monkeypatch):
    fake_supabase = FakeSupabase("50.00")
    client = build_client(monkeypatch, fake_supabase)

    response = client.post(
        "/api/v1/run-sessions",
        json=VALID_PAYLOAD,
        headers=INTERNAL_SECRET_HEADER,
    )

    assert response.status_code == 402
    assert response.json()["code"] == "COST_LIMIT_REACHED"
    assert fake_supabase.inserted_runs == []
    assert fake_supabase.inserted_qualifiers == []


def test_run_session_missing_secret_returns_401(monkeypatch):
    fake_supabase = FakeSupabase("1.00")
    client = build_client(monkeypatch, fake_supabase)

    response = client.post("/api/v1/run-sessions", json=VALID_PAYLOAD)

    assert response.status_code == 401
    assert response.json()["code"] == "UNAUTHORIZED"


def test_run_session_wrong_secret_returns_401(monkeypatch):
    fake_supabase = FakeSupabase("1.00")
    client = build_client(monkeypatch, fake_supabase)

    response = client.post(
        "/api/v1/run-sessions",
        json=VALID_PAYLOAD,
        headers={"X-Internal-Secret": "wrong-secret"},
    )

    assert response.status_code == 401
    assert response.json()["code"] == "UNAUTHORIZED"


def test_run_session_validation_failure(monkeypatch):
    fake_supabase = FakeSupabase("1.00")
    client = build_client(monkeypatch, fake_supabase)

    response = client.post(
        "/api/v1/run-sessions",
        json={**VALID_PAYLOAD, "topic": "   "},
        headers=INTERNAL_SECRET_HEADER,
    )

    assert response.status_code == 422
    assert fake_supabase.inserted_runs == []
