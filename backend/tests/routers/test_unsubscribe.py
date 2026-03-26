from __future__ import annotations

import importlib
from datetime import UTC, datetime

from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.core.database import get_supabase_client
from app.services.email_service import _generate_unsubscribe_token

_TEST_SECRET = "test-internal-secret"
_TEST_USER_ID = "11111111-1111-4111-8111-111111111111"
_VALID_TOKEN = _generate_unsubscribe_token(_TEST_USER_ID, _TEST_SECRET)


class FakeResponse:
    def __init__(self, data):
        self.data = data


class FakeQuery:
    def __init__(self, supabase):
        self._supabase = supabase
        self._table_name: str | None = None
        self._select_columns: list[str] | None = None
        self._payload: dict[str, object] | None = None
        self._id_filter: str | None = None
        self._is_filters: dict[str, object] = {}
        self._email_filter: str | None = None
        self._mode: str = "update"

    def select(self, columns: str):
        self._mode = "select"
        self._select_columns = [part.strip() for part in columns.split(",")]
        return self

    def update(self, payload: dict[str, object]):
        self._mode = "update"
        self._payload = payload
        return self

    def delete(self):
        self._mode = "delete"
        return self

    def eq(self, field: str, value: object):
        if field == "id" and isinstance(value, str):
            self._id_filter = value
        if field == "email" and isinstance(value, str):
            self._email_filter = value
        return self

    def is_(self, field: str, value: object):
        self._is_filters[field] = value
        return self

    def limit(self, _value: int):
        return self

    def execute(self):
        if self._mode == "select":
            selected: list[dict[str, object]] = []
            for row in self._supabase.users:
                if self._id_filter is not None and row.get("id") != self._id_filter:
                    continue
                if self._select_columns is None:
                    selected.append(dict(row))
                else:
                    selected.append(
                        {
                            key: row.get(key)
                            for key in self._select_columns
                            if key in ("id", "email", "unsubscribed_at")
                        }
                    )
            return FakeResponse(selected)

        if self._mode == "delete":
            if self._email_filter is None:
                return FakeResponse([])
            deleted = [
                dict(row)
                for row in self._supabase.waitlist
                if row.get("email") == self._email_filter
            ]
            self._supabase.waitlist = [
                row
                for row in self._supabase.waitlist
                if row.get("email") != self._email_filter
            ]
            return FakeResponse(deleted)

        updated: list[dict[str, object]] = []
        for row in self._supabase.users:
            if self._id_filter is not None and row.get("id") != self._id_filter:
                continue
            if (
                self._is_filters.get("unsubscribed_at") == "null"
                and row.get("unsubscribed_at") is not None
            ):
                continue
            assert self._payload is not None
            row.update(self._payload)
            updated.append(dict(row))
        return FakeResponse(updated)


class FakeSupabase:
    def __init__(self):
        self.users = [
            {
                "id": "11111111-1111-4111-8111-111111111111",
                "email": "user@example.com",
                "unsubscribed_at": None,
            }
        ]
        self.waitlist = [{"email": "user@example.com"}]

    def table(self, table_name: str):
        assert table_name in {"users", "waitlist"}
        query = FakeQuery(self)
        query._table_name = table_name
        return query


def build_client(monkeypatch, fake_supabase: FakeSupabase) -> TestClient:
    monkeypatch.setenv("SWARMSENSE_SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setenv("SWARMSENSE_SUPABASE_SERVICE_KEY", "service-key")
    monkeypatch.setenv("SWARMSENSE_KIMI_API_KEY", "kimi-key")
    monkeypatch.setenv("SWARMSENSE_OPENROUTER_API_KEY", "or_test")
    monkeypatch.setenv("SWARMSENSE_OPERATOR_API_KEY", "operator-key")
    monkeypatch.setenv("SWARMSENSE_INTERNAL_SECRET", "test-internal-secret")
    monkeypatch.setenv("SWARMSENSE_ENVIRONMENT", "development")
    monkeypatch.setenv("SWARMSENSE_FRONTEND_ORIGIN", "https://swarmsense.vercel.app")
    monkeypatch.setenv("SWARMSENSE_BACKEND_ORIGIN", "https://api.swarmsense.ai")
    monkeypatch.setenv("SWARMSENSE_RESEND_API_KEY", "re_key")
    monkeypatch.setenv("SWARMSENSE_EMAIL_FROM", "SwarmSense <noreply@swarmsense.ai>")
    monkeypatch.setenv("SWARMSENSE_EMAIL_REPLY_TO", "support@swarmsense.ai")

    get_settings.cache_clear()
    get_supabase_client.cache_clear()
    import app.main as main
    import app.routers.unsubscribe as unsubscribe_router

    importlib.reload(unsubscribe_router)
    importlib.reload(main)
    def _mark_user_unsubscribed(*, user_id: str) -> None:
        for row in fake_supabase.users:
            if row.get("id") == user_id and row.get("unsubscribed_at") is None:
                row["unsubscribed_at"] = datetime.now(UTC).isoformat()
        matched_emails = {
            row["email"] for row in fake_supabase.users if row.get("id") == user_id
        }
        fake_supabase.waitlist = [
            row for row in fake_supabase.waitlist if row.get("email") not in matched_emails
        ]

    monkeypatch.setattr(unsubscribe_router, "mark_user_unsubscribed", _mark_user_unsubscribed)

    return TestClient(main.app)


def test_unsubscribe_sets_unsubscribed_at(monkeypatch):
    fake_supabase = FakeSupabase()
    client = build_client(monkeypatch, fake_supabase)

    response = client.post(
        "/api/v1/unsubscribe",
        json={"user_id": _TEST_USER_ID, "token": _VALID_TOKEN},
    )

    assert response.status_code == 200
    assert response.json() == {"status": "unsubscribed"}
    assert fake_supabase.users[0]["unsubscribed_at"] is not None
    assert fake_supabase.waitlist == []


def test_unsubscribe_rejects_invalid_token(monkeypatch):
    fake_supabase = FakeSupabase()
    client = build_client(monkeypatch, fake_supabase)

    response = client.post(
        "/api/v1/unsubscribe",
        json={"user_id": _TEST_USER_ID, "token": "badbadtoken"},
    )

    assert response.status_code == 400
    assert fake_supabase.users[0]["unsubscribed_at"] is None
    assert len(fake_supabase.waitlist) == 1


def test_unsubscribe_is_idempotent(monkeypatch):
    fake_supabase = FakeSupabase()
    fake_supabase.users[0]["unsubscribed_at"] = datetime.now(UTC).isoformat()
    client = build_client(monkeypatch, fake_supabase)

    response = client.post(
        "/api/v1/unsubscribe",
        json={"user_id": _TEST_USER_ID, "token": _VALID_TOKEN},
    )

    assert response.status_code == 200
    assert response.json() == {"status": "unsubscribed"}


def test_unsubscribe_link_get_is_functional(monkeypatch):
    fake_supabase = FakeSupabase()
    client = build_client(monkeypatch, fake_supabase)

    response = client.get(
        f"/api/v1/unsubscribe?user_id={_TEST_USER_ID}&token={_VALID_TOKEN}"
    )

    assert response.status_code == 200
    assert "leiratkozt" in response.text.lower()
    assert fake_supabase.users[0]["unsubscribed_at"] is not None


def test_unsubscribe_link_get_rejects_invalid_token(monkeypatch):
    fake_supabase = FakeSupabase()
    client = build_client(monkeypatch, fake_supabase)

    response = client.get(
        f"/api/v1/unsubscribe?user_id={_TEST_USER_ID}&token=wrongtoken"
    )

    assert response.status_code == 400
    assert fake_supabase.users[0]["unsubscribed_at"] is None
