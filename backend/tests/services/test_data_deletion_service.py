from __future__ import annotations

from typing import Any

import pytest

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

        if self._operation == "select":
            if self._limit is not None:
                return FakeResponse([dict(row) for row in filtered[: self._limit]])
            return FakeResponse([dict(row) for row in filtered])

        self._supabase.tables[self._table_name] = [
            row
            for row in rows
            if not all(
                row.get(field) == value for field, value in self._filters_eq.items()
            )
        ]
        return FakeResponse([dict(row) for row in filtered])


class FakeSupabase:
    def __init__(self):
        self.tables: dict[str, list[dict[str, Any]]] = {
            "users": [
                {
                    "id": "user-1",
                    "email": "user@example.com",
                    "unsubscribed_at": "2026-03-20T12:00:00Z",
                }
            ],
            "runs": [
                {"id": "run-1", "user_id": "user-1", "status": "completed"},
                {"id": "run-2", "user_id": "user-1", "status": "partial"},
            ],
            "qualifier_responses": [
                {"id": "qr-1", "run_id": "run-1", "user_id": "user-1"},
                {"id": "qr-2", "run_id": "run-2", "user_id": "user-1"},
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


def test_delete_user_data_by_email_removes_related_records(monkeypatch) -> None:
    fake_supabase = FakeSupabase()
    monkeypatch.setattr(
        data_deletion_service, "get_supabase_client", lambda: fake_supabase
    )

    result = data_deletion_service.delete_user_data_by_email(
        email="  User@Example.com ",
        confirm=True,
    )

    assert result.user_found is True
    assert result.deleted_rows == {
        "qualifier_responses": 2,
        "runs": 2,
        "magic_link_tokens": 1,
        "waitlist": 1,
        "users": 1,
    }
    assert fake_supabase.tables["users"] == []
    assert fake_supabase.tables["runs"] == []
    assert fake_supabase.tables["qualifier_responses"] == []
    assert fake_supabase.tables["magic_link_tokens"] == []
    assert fake_supabase.tables["waitlist"] == []


def test_delete_user_data_by_email_dry_run_reports_counts_only(monkeypatch) -> None:
    fake_supabase = FakeSupabase()
    monkeypatch.setattr(
        data_deletion_service, "get_supabase_client", lambda: fake_supabase
    )

    result = data_deletion_service.delete_user_data_by_email(
        email="user@example.com",
        confirm=True,
        dry_run=True,
    )

    assert result.dry_run is True
    assert result.deleted_rows == {
        "qualifier_responses": 2,
        "runs": 2,
        "magic_link_tokens": 1,
        "waitlist": 1,
        "users": 1,
    }
    assert len(fake_supabase.tables["users"]) == 1
    assert len(fake_supabase.tables["runs"]) == 2
    assert len(fake_supabase.tables["qualifier_responses"]) == 2


def test_delete_user_data_by_email_is_idempotent_for_missing_user(monkeypatch) -> None:
    fake_supabase = FakeSupabase()
    monkeypatch.setattr(
        data_deletion_service, "get_supabase_client", lambda: fake_supabase
    )

    first = data_deletion_service.delete_user_data_by_email(
        email="user@example.com",
        confirm=True,
    )
    second = data_deletion_service.delete_user_data_by_email(
        email="user@example.com",
        confirm=True,
    )

    assert first.user_found is True
    assert second.user_found is False
    assert second.deleted_rows == {
        "qualifier_responses": 0,
        "runs": 0,
        "magic_link_tokens": 0,
        "waitlist": 0,
        "users": 0,
    }


def test_delete_user_data_by_email_requires_confirmation() -> None:
    with pytest.raises(ValueError, match="requires explicit confirmation"):
        data_deletion_service.delete_user_data_by_email(
            email="user@example.com",
            confirm=False,
        )


def test_normalize_and_validate_email_rejects_invalid_email() -> None:
    with pytest.raises(ValueError, match="Invalid email format"):
        data_deletion_service.normalize_and_validate_email("not-an-email")
