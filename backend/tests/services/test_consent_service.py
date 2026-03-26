from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from app.services import consent_service


class FakeResponse:
    def __init__(self, data: list[dict[str, Any]]):
        self.data = data


class FakeQuery:
    def __init__(self, supabase, table_name: str):
        self._supabase = supabase
        self._table_name = table_name
        self._mode = "select"
        self._filters: dict[str, Any] = {}
        self._payload: dict[str, Any] | None = None
        self._select_fields: tuple[str, ...] | None = None
        self._ilike_filters: dict[str, str] = {}

    def select(self, fields: str):
        self._mode = "select"
        self._select_fields = tuple(part.strip() for part in fields.split(","))
        return self

    def eq(self, field: str, value: Any):
        self._filters[field] = value
        return self

    def ilike(self, field: str, pattern: str):
        self._ilike_filters[field] = pattern
        return self

    def is_(self, _field: str, _value: Any):
        return self

    def update(self, payload: dict[str, Any]):
        self._mode = "update"
        self._payload = payload
        return self

    def delete(self):
        self._mode = "delete"
        return self

    def limit(self, _value: int):
        return self

    def execute(self):
        table = self._supabase.tables[self._table_name]
        matched = [
            row
            for row in table
            if all(row.get(field) == value for field, value in self._filters.items())
        ]
        for field, pattern in self._ilike_filters.items():
            matched = [
                row
                for row in matched if str(row.get(field, "")).lower() == pattern.lower()
            ]
        if self._mode == "select":
            if self._select_fields is None:
                return FakeResponse([dict(row) for row in matched[:1]])
            selected = [
                {field: row.get(field) for field in self._select_fields if field}
                for row in matched[:1]
            ]
            return FakeResponse(selected)
        if self._mode == "update":
            assert self._payload is not None
            for row in matched:
                row.update(self._payload)
            return FakeResponse([dict(row) for row in matched])
        if self._mode == "delete":
            self._supabase.tables[self._table_name] = [
                row for row in table if row not in matched
            ]
            return FakeResponse([dict(row) for row in matched])
        return FakeResponse([])


class FakeSupabase:
    def __init__(self):
        self.tables = {
            "users": [
                {"id": "u-1", "email": "user@example.com", "unsubscribed_at": None}
            ],
            "waitlist": [{"email": "user@example.com"}],
        }

    def table(self, table_name: str):
        return FakeQuery(self, table_name)


def test_is_marketing_email_allowed(monkeypatch) -> None:
    fake = FakeSupabase()
    monkeypatch.setattr(consent_service, "get_supabase_client", lambda: fake)

    assert consent_service.is_marketing_email_allowed(user_id="u-1") is True
    fake.tables["users"][0]["unsubscribed_at"] = datetime.now(UTC).isoformat()
    assert consent_service.is_marketing_email_allowed(user_id="u-1") is False


def test_mark_user_unsubscribed_updates_user_and_waitlist(monkeypatch) -> None:
    fake = FakeSupabase()
    monkeypatch.setattr(consent_service, "get_supabase_client", lambda: fake)

    consent_service.mark_user_unsubscribed(user_id="u-1")

    assert fake.tables["users"][0]["unsubscribed_at"] is not None
    assert fake.tables["waitlist"] == []


def test_mark_user_unsubscribed_removes_case_variant_waitlist_email(monkeypatch) -> None:
    fake = FakeSupabase()
    fake.tables["users"][0]["email"] = "User@Example.com"
    fake.tables["waitlist"] = [{"email": "User@Example.com"}]
    monkeypatch.setattr(consent_service, "get_supabase_client", lambda: fake)

    consent_service.mark_user_unsubscribed(user_id="u-1")

    assert fake.tables["users"][0]["unsubscribed_at"] is not None
    assert fake.tables["waitlist"] == []
