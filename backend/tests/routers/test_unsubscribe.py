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
        self._payload: dict[str, object] | None = None
        self._id_filter: str | None = None
        self._is_filters: dict[str, object] = {}

    def update(self, payload: dict[str, object]):
        self._payload = payload
        return self

    def eq(self, field: str, value: object):
        if field == "id" and isinstance(value, str):
            self._id_filter = value
        return self

    def is_(self, field: str, value: object):
        self._is_filters[field] = value
        return self

    def execute(self):
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

    def table(self, table_name: str):
        assert table_name == "users"
        return FakeQuery(self)


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
    monkeypatch.setattr(
        unsubscribe_router, "get_supabase_client", lambda: fake_supabase
    )

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


def test_unsubscribe_rejects_invalid_token(monkeypatch):
    fake_supabase = FakeSupabase()
    client = build_client(monkeypatch, fake_supabase)

    response = client.post(
        "/api/v1/unsubscribe",
        json={"user_id": _TEST_USER_ID, "token": "badbadtoken"},
    )

    assert response.status_code == 400
    assert fake_supabase.users[0]["unsubscribed_at"] is None


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
