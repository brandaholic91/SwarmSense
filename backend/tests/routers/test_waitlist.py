from __future__ import annotations

import importlib

from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.core.database import get_supabase_client


class DuplicateEmailError(Exception):
    code = "23505"


class FakeResponse:
    def __init__(self, data):
        self.data = data


class FakeQuery:
    def __init__(self, supabase, table_name: str):
        self._supabase = supabase
        self._table_name = table_name
        self._payload: dict[str, object] | None = None
        self._operation = "select"

    def insert(self, payload: dict[str, object]):
        self._operation = "insert"
        self._payload = payload
        return self

    def execute(self):
        if self._table_name != "waitlist" or self._operation != "insert":
            return FakeResponse([])

        assert self._payload is not None
        if self._supabase.raise_generic:
            raise RuntimeError("db down")

        email = str(self._payload["email"])
        if email in self._supabase.waitlist:
            raise DuplicateEmailError("duplicate key value violates unique constraint")

        self._supabase.waitlist.add(email)
        return FakeResponse([{"email": email}])


class FakeSupabase:
    def __init__(self):
        self.waitlist: set[str] = set()
        self.raise_generic = False

    def table(self, table_name: str) -> FakeQuery:
        return FakeQuery(self, table_name)


def build_client(monkeypatch, fake_supabase: FakeSupabase) -> TestClient:
    monkeypatch.setenv("SWARMSENSE_SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setenv("SWARMSENSE_SUPABASE_SERVICE_KEY", "service-key")
    monkeypatch.setenv("SWARMSENSE_KIMI_API_KEY", "kimi-key")
    monkeypatch.setenv("SWARMSENSE_OPERATOR_API_KEY", "operator-key")
    monkeypatch.setenv("SWARMSENSE_ENVIRONMENT", "development")
    monkeypatch.setenv("SWARMSENSE_FRONTEND_ORIGIN", "https://swarmsense.vercel.app")
    monkeypatch.setenv("SWARMSENSE_RESEND_API_KEY", "re_key")
    monkeypatch.setenv("SWARMSENSE_EMAIL_FROM", "SwarmSense <noreply@swarmsense.ai>")
    monkeypatch.setenv("SWARMSENSE_EMAIL_REPLY_TO", "support@swarmsense.ai")

    get_settings.cache_clear()
    get_supabase_client.cache_clear()
    import app.main as main
    import app.routers.waitlist as waitlist_router

    importlib.reload(waitlist_router)
    importlib.reload(main)
    monkeypatch.setattr(waitlist_router, "get_supabase_client", lambda: fake_supabase)

    return TestClient(main.app)


def test_waitlist_creates_new_signup(monkeypatch):
    fake_supabase = FakeSupabase()
    client = build_client(monkeypatch, fake_supabase)

    response = client.post("/api/v1/waitlist", json={"email": "  User@Example.com "})

    assert response.status_code == 200
    assert response.json() == {"status": "joined"}
    assert "user@example.com" in fake_supabase.waitlist


def test_waitlist_duplicate_returns_idempotent_success(monkeypatch):
    fake_supabase = FakeSupabase()
    fake_supabase.waitlist.add("user@example.com")
    client = build_client(monkeypatch, fake_supabase)

    response = client.post("/api/v1/waitlist", json={"email": "user@example.com"})

    assert response.status_code == 200
    assert response.json() == {"status": "already_joined"}


def test_waitlist_rejects_invalid_email(monkeypatch):
    fake_supabase = FakeSupabase()
    client = build_client(monkeypatch, fake_supabase)

    response = client.post("/api/v1/waitlist", json={"email": "invalid-email"})

    assert response.status_code == 422


def test_waitlist_returns_error_contract_on_server_failure(monkeypatch):
    fake_supabase = FakeSupabase()
    fake_supabase.raise_generic = True
    client = build_client(monkeypatch, fake_supabase)

    response = client.post("/api/v1/waitlist", json={"email": "user@example.com"})

    assert response.status_code == 500
    assert response.json() == {
        "detail": "Failed to join waitlist",
        "code": "WAITLIST_SIGNUP_FAILED",
    }
