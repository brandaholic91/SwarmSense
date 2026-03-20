from __future__ import annotations

import importlib

from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.core.database import get_supabase_client


class FakeResponse:
    def __init__(self, data):
        self.data = data


class FakeQuery:
    def __init__(self, supabase, table_name):
        self._supabase = supabase
        self._table_name = table_name
        self._filters: dict[str, object] = {}

    def select(self, _fields: str):
        return self

    def eq(self, field: str, value: object):
        self._filters[field] = value
        return self

    def in_(self, field: str, values: list[str]):
        self._filters[field] = values
        return self

    def limit(self, _n: int):
        return self

    def execute(self):
        if self._table_name == "users":
            email = self._filters.get("email")
            self._supabase.last_email_lookup = email
            user_id = self._supabase.users_by_email.get(email)
            return FakeResponse([] if user_id is None else [{"id": user_id}])

        if self._table_name == "runs":
            user_id = self._filters.get("user_id")
            statuses = self._filters.get("status", [])
            has_completed_status = any(
                status in {"completed", "partial"} for status in statuses
            )
            if (
                has_completed_status
                and user_id in self._supabase.users_with_completed_runs
            ):
                return FakeResponse([{"id": "run-1"}])
            return FakeResponse([])

        return FakeResponse([])


class FakeSupabase:
    def __init__(
        self, users_by_email: dict[str, str], users_with_completed_runs: set[str]
    ):
        self.users_by_email = users_by_email
        self.users_with_completed_runs = users_with_completed_runs
        self.last_email_lookup: str | None = None

    def table(self, table_name: str) -> FakeQuery:
        return FakeQuery(self, table_name)


def build_client(monkeypatch, fake_supabase: FakeSupabase) -> TestClient:
    monkeypatch.setenv("SWARMSENSE_SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setenv("SWARMSENSE_SUPABASE_SERVICE_KEY", "service-key")
    monkeypatch.setenv("SWARMSENSE_KIMI_API_KEY", "kimi-key")
    monkeypatch.setenv("SWARMSENSE_OPERATOR_API_KEY", "operator-key")
    monkeypatch.setenv("SWARMSENSE_ENVIRONMENT", "development")
    monkeypatch.setenv("SWARMSENSE_FRONTEND_ORIGIN", "https://swarmsense.vercel.app")

    get_settings.cache_clear()
    get_supabase_client.cache_clear()
    import app.main as main
    import app.routers.auth as auth_router

    importlib.reload(auth_router)
    importlib.reload(main)
    monkeypatch.setattr(auth_router, "get_supabase_client", lambda: fake_supabase)

    return TestClient(main.app)


def test_check_email_normalizes_at_input_boundary(monkeypatch):
    fake_supabase = FakeSupabase(users_by_email={}, users_with_completed_runs=set())
    client = build_client(monkeypatch, fake_supabase)

    response = client.post(
        "/api/v1/auth/check-email",
        json={
            "email": "  Teszt@Example.HU  ",
            "has_consent": True,
            "consent_timestamp": "2026-03-20T18:00:00Z",
        },
    )

    assert response.status_code == 200
    assert response.json() == {"status": "new"}
    assert fake_supabase.last_email_lookup == "teszt@example.hu"


def test_check_email_returns_new_for_unknown_email(monkeypatch):
    fake_supabase = FakeSupabase(users_by_email={}, users_with_completed_runs=set())
    client = build_client(monkeypatch, fake_supabase)

    response = client.post(
        "/api/v1/auth/check-email",
        json={
            "email": "new-user@example.com",
            "has_consent": True,
            "consent_timestamp": "2026-03-20T18:00:00Z",
        },
    )

    assert response.status_code == 200
    assert response.json() == {"status": "new"}


def test_check_email_returns_returning_for_user_with_completed_run(monkeypatch):
    fake_supabase = FakeSupabase(
        users_by_email={"user@example.com": "user-1"},
        users_with_completed_runs={"user-1"},
    )
    client = build_client(monkeypatch, fake_supabase)

    response = client.post(
        "/api/v1/auth/check-email",
        json={
            "email": "user@example.com",
            "has_consent": True,
            "consent_timestamp": "2026-03-20T18:00:00Z",
        },
    )

    assert response.status_code == 200
    assert response.json() == {"status": "returning", "redirect_to": "/blocked"}


def test_check_email_rejects_invalid_email(monkeypatch):
    fake_supabase = FakeSupabase(users_by_email={}, users_with_completed_runs=set())
    client = build_client(monkeypatch, fake_supabase)

    response = client.post(
        "/api/v1/auth/check-email",
        json={
            "email": "not-an-email",
            "has_consent": True,
            "consent_timestamp": "2026-03-20T18:00:00Z",
        },
    )

    assert response.status_code == 422
