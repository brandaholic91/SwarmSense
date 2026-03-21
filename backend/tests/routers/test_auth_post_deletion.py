from __future__ import annotations

import importlib
from typing import Any

from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.core.database import get_supabase_client
from app.services import data_deletion_service


class FakeResponse:
    def __init__(self, data: list[dict[str, Any]]):
        self.data = data


class FakeQuery:
    def __init__(self, supabase: "FakeSupabase", table_name: str):
        self._supabase = supabase
        self._table_name = table_name
        self._operation = "select"
        self._filters_eq: dict[str, Any] = {}
        self._filters_in: dict[str, list[str]] = {}
        self._limit: int | None = None

    def select(self, _fields: str):
        self._operation = "select"
        return self

    def delete(self):
        self._operation = "delete"
        return self

    def eq(self, field: str, value: Any):
        self._filters_eq[field] = value
        return self

    def in_(self, field: str, values: list[str]):
        self._filters_in[field] = values
        return self

    def limit(self, value: int):
        self._limit = value
        return self

    def execute(self) -> FakeResponse:
        rows = self._supabase.tables[self._table_name]
        filtered = [
            row
            for row in rows
            if all(row.get(field) == value for field, value in self._filters_eq.items())
        ]
        for field, values in self._filters_in.items():
            filtered = [row for row in filtered if row.get(field) in values]

        if self._operation == "select":
            if self._limit is not None:
                return FakeResponse([dict(row) for row in filtered[: self._limit]])
            return FakeResponse([dict(row) for row in filtered])

        self._supabase.tables[self._table_name] = [
            row for row in rows if row not in filtered
        ]
        return FakeResponse([dict(row) for row in filtered])


class FakeSupabase:
    def __init__(self):
        self.tables: dict[str, list[dict[str, Any]]] = {
            "users": [
                {
                    "id": "user-1",
                    "email": "user@example.com",
                    "unsubscribed_at": "2026-03-20T10:00:00Z",
                }
            ],
            "runs": [{"id": "run-1", "user_id": "user-1", "status": "completed"}],
            "qualifier_responses": [
                {"id": "qr-1", "run_id": "run-1", "user_id": "user-1"}
            ],
            "magic_link_tokens": [
                {
                    "token": "11111111-1111-4111-8111-111111111111",
                    "user_id": "user-1",
                }
            ],
            "waitlist": [{"id": "w-1", "email": "user@example.com"}],
        }

    def table(self, table_name: str) -> FakeQuery:
        return FakeQuery(self, table_name)


def build_client(monkeypatch, fake_supabase: FakeSupabase) -> TestClient:
    monkeypatch.setenv("SWARMSENSE_SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setenv("SWARMSENSE_SUPABASE_SERVICE_KEY", "service-key")
    monkeypatch.setenv("SWARMSENSE_KIMI_API_KEY", "kimi-key")
    monkeypatch.setenv("SWARMSENSE_OPENROUTER_API_KEY", "or_test")
    monkeypatch.setenv("SWARMSENSE_OPERATOR_API_KEY", "operator-key")
    monkeypatch.setenv("SWARMSENSE_INTERNAL_SECRET", "test-internal-secret")
    monkeypatch.setenv("SWARMSENSE_ENVIRONMENT", "development")
    monkeypatch.setenv("SWARMSENSE_BACKEND_ORIGIN", "https://api.swarmsense.ai")
    monkeypatch.setenv("SWARMSENSE_FRONTEND_ORIGIN", "https://swarmsense.vercel.app")
    monkeypatch.setenv("SWARMSENSE_RESEND_API_KEY", "re_key")
    monkeypatch.setenv("SWARMSENSE_EMAIL_FROM", "SwarmSense <noreply@swarmsense.ai>")
    monkeypatch.setenv("SWARMSENSE_EMAIL_REPLY_TO", "support@swarmsense.ai")

    get_settings.cache_clear()
    get_supabase_client.cache_clear()
    import app.main as main
    import app.routers.auth as auth_router

    importlib.reload(auth_router)
    importlib.reload(main)
    monkeypatch.setattr(auth_router, "get_supabase_client", lambda: fake_supabase)
    monkeypatch.setattr(
        data_deletion_service, "get_supabase_client", lambda: fake_supabase
    )

    return TestClient(main.app)


def _check_email(client: TestClient, email: str) -> dict[str, Any]:
    response = client.post(
        "/api/v1/auth/check-email",
        json={
            "email": email,
            "has_consent": True,
            "consent_timestamp": "2026-03-20T18:00:00Z",
        },
    )
    assert response.status_code == 200
    return response.json()


def test_check_email_returns_new_after_data_deletion(monkeypatch) -> None:
    fake_supabase = FakeSupabase()
    client = build_client(monkeypatch, fake_supabase)

    before = _check_email(client, "user@example.com")
    assert before == {"status": "returning", "redirect_to": "/blocked"}

    result = data_deletion_service.delete_user_data_by_email(
        email="user@example.com",
        confirm=True,
    )

    assert result.deleted_rows["users"] == 1
    after = _check_email(client, "user@example.com")
    assert after == {"status": "new"}


def test_check_email_stays_new_with_waitlist_or_unsubscribe_artifacts(
    monkeypatch,
) -> None:
    fake_supabase = FakeSupabase()
    client = build_client(monkeypatch, fake_supabase)

    data_deletion_service.delete_user_data_by_email(
        email="user@example.com", confirm=True
    )

    fake_supabase.tables["waitlist"].append({"id": "w-2", "email": "user@example.com"})
    fake_supabase.tables["magic_link_tokens"].append(
        {"token": "22222222-2222-4222-8222-222222222222", "user_id": "deleted-user"}
    )

    response_body = _check_email(client, "user@example.com")
    assert response_body == {"status": "new"}
