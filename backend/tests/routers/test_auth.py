from __future__ import annotations

import importlib
from datetime import UTC, datetime, timedelta
from uuid import UUID

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
        self._in_filters: dict[str, list[str]] = {}
        self._is_filters: dict[str, object] = {}
        self._operation = "select"
        self._payload: dict[str, object] | None = None

    def select(self, _fields: str):
        self._operation = "select"
        return self

    def eq(self, field: str, value: object):
        self._filters[field] = value
        return self

    def in_(self, field: str, values: list[str]):
        self._in_filters[field] = values
        return self

    def is_(self, field: str, value: object):
        self._is_filters[field] = value
        return self

    def limit(self, _n: int):
        return self

    def insert(self, payload: dict[str, object]):
        self._operation = "insert"
        self._payload = payload
        return self

    def update(self, payload: dict[str, object]):
        self._operation = "update"
        self._payload = payload
        return self

    def execute(self):
        if self._table_name == "users":
            return self._execute_users()
        if self._table_name == "runs":
            return self._execute_runs()
        if self._table_name == "magic_link_tokens":
            return self._execute_magic_link_tokens()
        return FakeResponse([])

    def _execute_users(self):
        if self._operation == "insert":
            assert self._payload is not None
            email = str(self._payload["email"])
            user_id = f"user-{len(self._supabase.user_records) + 1}"
            record = {
                "id": user_id,
                "email": email,
                "has_consent": self._payload["has_consent"],
                "consent_timestamp": self._payload["consent_timestamp"],
            }
            self._supabase.user_records[email] = record
            self._supabase.users_by_email[email] = user_id
            return FakeResponse([{"id": user_id}])

        if self._operation == "update":
            assert self._payload is not None
            user_id = self._filters.get("id")
            if not isinstance(user_id, str):
                return FakeResponse([])
            for record in self._supabase.user_records.values():
                if record.get("id") == user_id:
                    record.update(self._payload)
                    return FakeResponse([record])
            return FakeResponse([])

        email = self._filters.get("email")
        self._supabase.last_email_lookup = email
        if not isinstance(email, str):
            return FakeResponse([])
        user_record = self._supabase.user_records.get(email)
        if user_record is None:
            return FakeResponse([])
        return FakeResponse([{"id": user_record["id"]}])

    def _execute_runs(self):
        user_id = self._filters.get("user_id")
        statuses = self._in_filters.get("status", [])
        has_completed_status = any(
            status_name in {"completed", "partial"} for status_name in statuses
        )
        if has_completed_status and user_id in self._supabase.users_with_completed_runs:
            return FakeResponse([{"id": "run-1"}])
        return FakeResponse([])

    def _execute_magic_link_tokens(self):
        if self._operation == "insert":
            assert self._payload is not None
            token = str(self._payload["token"])
            token_record = {
                "token": token,
                "user_id": self._payload["user_id"],
                "expires_at": self._payload["expires_at"],
                "used_at": self._payload["used_at"],
            }
            self._supabase.magic_link_tokens[token] = token_record
            return FakeResponse([token_record])

        if self._operation == "update":
            assert self._payload is not None
            token_filter = self._filters.get("token")
            user_id_filter = self._filters.get("user_id")
            requires_unused = self._is_filters.get("used_at") == "null"

            if token_filter is not None:
                # Single token update (verify path or expired token mark)
                token_record = self._supabase.magic_link_tokens.get(str(token_filter))
                if token_record is None:
                    return FakeResponse([])
                if requires_unused and token_record.get("used_at") is not None:
                    return FakeResponse([])
                token_record.update(self._payload)
                return FakeResponse([token_record])

            if user_id_filter is not None:
                # Batch invalidation by user_id (new token issuance path)
                updated = []
                for token_record in self._supabase.magic_link_tokens.values():
                    if token_record.get("user_id") == user_id_filter:
                        if not requires_unused or token_record.get("used_at") is None:
                            token_record.update(self._payload)
                            updated.append(token_record)
                return FakeResponse(updated)

            return FakeResponse([])

        token = self._filters.get("token")
        if not isinstance(token, str):
            return FakeResponse([])
        token_record = self._supabase.magic_link_tokens.get(token)
        if token_record is None:
            return FakeResponse([])
        return FakeResponse([token_record])


class FakeSupabase:
    def __init__(
        self,
        users_by_email: dict[str, str],
        users_with_completed_runs: set[str],
        user_records: dict[str, dict[str, object]] | None = None,
        magic_link_tokens: dict[str, dict[str, object]] | None = None,
    ):
        self.users_by_email = users_by_email
        self.users_with_completed_runs = users_with_completed_runs
        self.user_records = user_records or {
            email: {
                "id": user_id,
                "email": email,
                "has_consent": True,
                "consent_timestamp": "2026-03-20T18:00:00Z",
            }
            for email, user_id in users_by_email.items()
        }
        self.magic_link_tokens = magic_link_tokens or {}
        self.last_email_lookup: str | None = None

    def table(self, table_name: str) -> FakeQuery:
        return FakeQuery(self, table_name)


def build_client(monkeypatch, fake_supabase: FakeSupabase) -> TestClient:
    monkeypatch.setenv("SWARMSENSE_SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setenv("SWARMSENSE_SUPABASE_SERVICE_KEY", "service-key")
    monkeypatch.setenv("SWARMSENSE_KIMI_API_KEY", "kimi-key")
    monkeypatch.setenv("SWARMSENSE_OPERATOR_API_KEY", "operator-key")
    monkeypatch.setenv("SWARMSENSE_INTERNAL_SECRET", "test-internal-secret")
    monkeypatch.setenv("SWARMSENSE_ENVIRONMENT", "development")
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


def test_check_email_rejects_missing_consent(monkeypatch):
    fake_supabase = FakeSupabase(users_by_email={}, users_with_completed_runs=set())
    client = build_client(monkeypatch, fake_supabase)

    response = client.post(
        "/api/v1/auth/check-email",
        json={
            "email": "user@example.com",
            "has_consent": False,
            "consent_timestamp": "2026-03-20T18:00:00Z",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Consent is required"


def test_check_email_rejects_naive_timestamp(monkeypatch):
    fake_supabase = FakeSupabase(users_by_email={}, users_with_completed_runs=set())
    client = build_client(monkeypatch, fake_supabase)

    response = client.post(
        "/api/v1/auth/check-email",
        json={
            "email": "user@example.com",
            "has_consent": True,
            "consent_timestamp": "2026-03-20T18:00:00",
        },
    )

    assert response.status_code == 422


def test_magic_link_creates_user_token_and_sends_email(monkeypatch):
    fake_supabase = FakeSupabase(users_by_email={}, users_with_completed_runs=set())
    client = build_client(monkeypatch, fake_supabase)
    import app.routers.auth as auth_router

    captured: dict[str, str] = {}

    def fake_send_magic_link_email(recipient_email: str, verify_url: str) -> None:
        captured["recipient"] = recipient_email
        captured["verify_url"] = verify_url

    monkeypatch.setattr(
        auth_router, "send_magic_link_email", fake_send_magic_link_email
    )

    before = datetime.now(UTC)
    response = client.post(
        "/api/v1/auth/magic-link",
        json={
            "email": "  Teszt@Example.HU  ",
            "has_consent": True,
            "consent_timestamp": "2026-03-20T18:00:00Z",
        },
    )
    after = datetime.now(UTC)

    assert response.status_code == 200
    assert response.json() == {"status": "sent"}

    created_user = fake_supabase.user_records.get("teszt@example.hu")
    assert created_user is not None
    assert created_user["has_consent"] is True
    # P-6: consent_timestamp must be server-side now(), not the request payload value
    stored_ts = datetime.fromisoformat(str(created_user["consent_timestamp"]))
    if stored_ts.tzinfo is None:
        stored_ts = stored_ts.replace(tzinfo=UTC)
    assert stored_ts >= before
    assert stored_ts <= after

    assert len(fake_supabase.magic_link_tokens) == 1
    token_record = list(fake_supabase.magic_link_tokens.values())[0]
    token = str(token_record["token"])
    UUID(token)
    expires_at = datetime.fromisoformat(str(token_record["expires_at"]))
    now = datetime.now(UTC)
    assert (
        now + timedelta(hours=23, minutes=59)
        <= expires_at
        <= now + timedelta(hours=24, minutes=1)
    )
    assert token_record["used_at"] is None

    assert captured["recipient"] == "teszt@example.hu"
    assert captured["verify_url"].startswith(
        "https://swarmsense.vercel.app/verify?token="
    )


def test_verify_marks_valid_token_as_used_and_returns_user_id(monkeypatch):
    token = "11111111-1111-4111-8111-111111111111"
    fake_supabase = FakeSupabase(
        users_by_email={"user@example.com": "user-1"},
        users_with_completed_runs=set(),
        magic_link_tokens={
            token: {
                "token": token,
                "user_id": "user-1",
                "expires_at": (datetime.now(UTC) + timedelta(hours=2)).isoformat(),
                "used_at": None,
            }
        },
    )
    client = build_client(monkeypatch, fake_supabase)

    response = client.post("/api/v1/auth/verify", json={"token": token})

    assert response.status_code == 200
    assert response.json() == {"user_id": "user-1"}
    assert fake_supabase.magic_link_tokens[token]["used_at"] is not None


def test_verify_returns_token_expired_for_expired_token(monkeypatch):
    token = "22222222-2222-4222-8222-222222222222"
    fake_supabase = FakeSupabase(
        users_by_email={"user@example.com": "user-1"},
        users_with_completed_runs=set(),
        magic_link_tokens={
            token: {
                "token": token,
                "user_id": "user-1",
                "expires_at": (datetime.now(UTC) - timedelta(minutes=1)).isoformat(),
                "used_at": None,
            }
        },
    )
    client = build_client(monkeypatch, fake_supabase)

    response = client.post("/api/v1/auth/verify", json={"token": token})

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Magic link token expired",
        "code": "TOKEN_EXPIRED",
    }


def test_verify_returns_token_invalid_for_used_or_unknown_token(monkeypatch):
    used_token = "33333333-3333-4333-8333-333333333333"
    unknown_token = "44444444-4444-4444-8444-444444444444"
    fake_supabase = FakeSupabase(
        users_by_email={"user@example.com": "user-1"},
        users_with_completed_runs=set(),
        magic_link_tokens={
            used_token: {
                "token": used_token,
                "user_id": "user-1",
                "expires_at": (datetime.now(UTC) + timedelta(hours=1)).isoformat(),
                "used_at": datetime.now(UTC).isoformat(),
            }
        },
    )
    client = build_client(monkeypatch, fake_supabase)

    used_response = client.post("/api/v1/auth/verify", json={"token": used_token})
    unknown_response = client.post("/api/v1/auth/verify", json={"token": unknown_token})

    assert used_response.status_code == 401
    assert used_response.json() == {
        "detail": "Magic link token invalid",
        "code": "TOKEN_INVALID",
    }
    assert unknown_response.status_code == 401
    assert unknown_response.json() == {
        "detail": "Magic link token invalid",
        "code": "TOKEN_INVALID",
    }


def test_magic_link_uses_server_side_consent_timestamp(monkeypatch):
    fake_supabase = FakeSupabase(users_by_email={}, users_with_completed_runs=set())
    client = build_client(monkeypatch, fake_supabase)
    import app.routers.auth as auth_router

    monkeypatch.setattr(auth_router, "send_magic_link_email", lambda *a: None)

    before = datetime.now(UTC)
    client.post(
        "/api/v1/auth/magic-link",
        json={
            "email": "new@example.com",
            "has_consent": True,
            "consent_timestamp": "2020-01-01T00:00:00Z",  # old payload timestamp
        },
    )
    after = datetime.now(UTC)

    created_user = fake_supabase.user_records.get("new@example.com")
    assert created_user is not None
    stored_ts = datetime.fromisoformat(str(created_user["consent_timestamp"]))
    if stored_ts.tzinfo is None:
        stored_ts = stored_ts.replace(tzinfo=UTC)
    assert before <= stored_ts <= after


def test_magic_link_invalidates_existing_unused_tokens(monkeypatch):
    old_token = "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"
    fake_supabase = FakeSupabase(
        users_by_email={"user@example.com": "user-1"},
        users_with_completed_runs=set(),
        magic_link_tokens={
            old_token: {
                "token": old_token,
                "user_id": "user-1",
                "expires_at": (datetime.now(UTC) + timedelta(hours=12)).isoformat(),
                "used_at": None,
            }
        },
    )
    client = build_client(monkeypatch, fake_supabase)
    import app.routers.auth as auth_router

    monkeypatch.setattr(auth_router, "send_magic_link_email", lambda *a: None)

    response = client.post(
        "/api/v1/auth/magic-link",
        json={
            "email": "user@example.com",
            "has_consent": True,
            "consent_timestamp": "2026-03-20T18:00:00Z",
        },
    )

    assert response.status_code == 200
    assert fake_supabase.magic_link_tokens[old_token]["used_at"] is not None
    assert len(fake_supabase.magic_link_tokens) == 2


def test_magic_link_updates_returning_user_consent(monkeypatch):
    fake_supabase = FakeSupabase(
        users_by_email={"returning@example.com": "user-5"},
        users_with_completed_runs=set(),
    )
    client = build_client(monkeypatch, fake_supabase)
    import app.routers.auth as auth_router

    monkeypatch.setattr(auth_router, "send_magic_link_email", lambda *a: None)

    before = datetime.now(UTC)
    response = client.post(
        "/api/v1/auth/magic-link",
        json={
            "email": "returning@example.com",
            "has_consent": True,
            "consent_timestamp": "2026-03-20T18:00:00Z",
        },
    )
    after = datetime.now(UTC)

    assert response.status_code == 200
    user = fake_supabase.user_records["returning@example.com"]
    stored_ts = datetime.fromisoformat(str(user["consent_timestamp"]))
    if stored_ts.tzinfo is None:
        stored_ts = stored_ts.replace(tzinfo=UTC)
    assert before <= stored_ts <= after


def test_verify_marks_expired_token_as_used(monkeypatch):
    token = "55555555-5555-4555-8555-555555555555"
    fake_supabase = FakeSupabase(
        users_by_email={"user@example.com": "user-1"},
        users_with_completed_runs=set(),
        magic_link_tokens={
            token: {
                "token": token,
                "user_id": "user-1",
                "expires_at": (datetime.now(UTC) - timedelta(minutes=1)).isoformat(),
                "used_at": None,
            }
        },
    )
    client = build_client(monkeypatch, fake_supabase)

    response = client.post("/api/v1/auth/verify", json={"token": token})

    assert response.status_code == 401
    assert response.json()["code"] == "TOKEN_EXPIRED"
    assert fake_supabase.magic_link_tokens[token]["used_at"] is not None
