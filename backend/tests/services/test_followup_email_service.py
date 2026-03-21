from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

from app.services import email_service


class FakeResponse:
    def __init__(self, data):
        self.data = data


class FakeQuery:
    def __init__(self, supabase, table_name: str):
        self._supabase = supabase
        self._table_name = table_name
        self._operation = "select"
        self._select_fields = ""
        self._filters_eq: dict[str, Any] = {}
        self._filters_in: dict[str, list[str]] = {}
        self._filters_lt: dict[str, str] = {}
        self._filters_is: dict[str, Any] = {}
        self._limit: int | None = None
        self._payload: dict[str, Any] | None = None

    def select(self, fields: str):
        self._operation = "select"
        self._select_fields = fields
        return self

    def eq(self, field: str, value: Any):
        self._filters_eq[field] = value
        return self

    def in_(self, field: str, values: list[str]):
        self._filters_in[field] = values
        return self

    def lt(self, field: str, value: str):
        self._filters_lt[field] = value
        return self

    def is_(self, field: str, value: Any):
        self._filters_is[field] = value
        return self

    def update(self, payload: dict[str, Any]):
        self._operation = "update"
        self._payload = payload
        return self

    def limit(self, value: int):
        self._limit = value
        return self

    def execute(self):
        if self._table_name == "runs" and self._operation == "select":
            rows = [dict(item) for item in self._supabase.runs]
            for field, value in self._filters_eq.items():
                rows = [row for row in rows if row.get(field) == value]
            for field, value in self._filters_in.items():
                rows = [row for row in rows if row.get(field) in value]
            for field, value in self._filters_lt.items():
                cutoff = datetime.fromisoformat(value.replace("Z", "+00:00"))
                rows = [
                    row
                    for row in rows
                    if isinstance(row.get(field), str)
                    and datetime.fromisoformat(str(row[field]).replace("Z", "+00:00"))
                    < cutoff
                ]
            return FakeResponse(rows)

        if self._table_name == "runs" and self._operation == "update":
            assert self._payload is not None
            updated: list[dict[str, Any]] = []
            for row in self._supabase.runs:
                if row.get("id") != self._filters_eq.get("id"):
                    continue
                for field, value in self._filters_eq.items():
                    if row.get(field) != value:
                        break
                else:
                    row.update(self._payload)
                    updated.append(dict(row))
            return FakeResponse(updated)

        if self._table_name == "users" and self._operation == "select":
            rows = [dict(item) for item in self._supabase.users]
            for field, value in self._filters_eq.items():
                rows = [row for row in rows if row.get(field) == value]
            if self._limit is not None:
                rows = rows[: self._limit]
            return FakeResponse(rows)

        if self._table_name == "users" and self._operation == "update":
            assert self._payload is not None
            updated: list[dict[str, Any]] = []
            for row in self._supabase.users:
                if row.get("id") != self._filters_eq.get("id"):
                    continue
                if (
                    self._filters_is.get("unsubscribed_at") == "null"
                    and row.get("unsubscribed_at") is not None
                ):
                    continue
                row.update(self._payload)
                updated.append(dict(row))
            return FakeResponse(updated)

        return FakeResponse([])


class FakeSupabase:
    def __init__(self, runs: list[dict[str, Any]], users: list[dict[str, Any]]):
        self.runs = runs
        self.users = users

    def table(self, name: str):
        return FakeQuery(self, name)


def test_dispatch_followups_sends_only_eligible_thresholds(monkeypatch) -> None:
    now = datetime.now(UTC)
    runs = [
        {
            "id": "run-day1",
            "user_id": "user-1",
            "status": "completed",
            "completed_at": (now - timedelta(days=2)).isoformat(),
            "day1_sent": False,
            "day3_sent": False,
            "day7_sent": False,
        },
        {
            "id": "run-day3",
            "user_id": "user-2",
            "status": "partial",
            "completed_at": (now - timedelta(days=4)).isoformat(),
            "day1_sent": True,
            "day3_sent": False,
            "day7_sent": False,
        },
        {
            "id": "run-too-early",
            "user_id": "user-3",
            "status": "completed",
            "completed_at": (now - timedelta(hours=12)).isoformat(),
            "day1_sent": False,
            "day3_sent": False,
            "day7_sent": False,
        },
    ]
    users = [
        {"id": "user-1", "email": "u1@example.com", "unsubscribed_at": None},
        {"id": "user-2", "email": "u2@example.com", "unsubscribed_at": None},
        {"id": "user-3", "email": "u3@example.com", "unsubscribed_at": None},
    ]
    fake_supabase = FakeSupabase(runs=runs, users=users)

    monkeypatch.setattr(email_service, "get_supabase_client", lambda: fake_supabase)

    sent: list[tuple[str, str]] = []
    monkeypatch.setattr(
        email_service,
        "send_followup_email",
        lambda *, recipient_email, day, user_id: sent.append((recipient_email, day)),
    )

    total = email_service.dispatch_followup_sequence()

    assert total == 2
    assert ("u1@example.com", "day1") in sent
    assert ("u2@example.com", "day3") in sent
    assert runs[0]["day1_sent"] is True
    assert runs[1]["day3_sent"] is True
    assert runs[2]["day1_sent"] is False


def test_dispatch_followups_skips_unsubscribed_users(monkeypatch) -> None:
    now = datetime.now(UTC)
    runs = [
        {
            "id": "run-1",
            "user_id": "user-1",
            "status": "completed",
            "completed_at": (now - timedelta(days=2)).isoformat(),
            "day1_sent": False,
            "day3_sent": False,
            "day7_sent": False,
        }
    ]
    users = [
        {
            "id": "user-1",
            "email": "u1@example.com",
            "unsubscribed_at": now.isoformat(),
        }
    ]
    fake_supabase = FakeSupabase(runs=runs, users=users)

    monkeypatch.setattr(email_service, "get_supabase_client", lambda: fake_supabase)

    sent: list[tuple[str, str]] = []
    monkeypatch.setattr(
        email_service,
        "send_followup_email",
        lambda *, recipient_email, day, user_id: sent.append((recipient_email, day)),
    )

    total = email_service.dispatch_followup_sequence()

    assert total == 0
    assert sent == []
    assert runs[0]["day1_sent"] is False


def test_dispatch_followups_does_not_mark_sent_on_provider_failure(monkeypatch) -> None:
    now = datetime.now(UTC)
    runs = [
        {
            "id": "run-1",
            "user_id": "user-1",
            "status": "completed",
            "completed_at": (now - timedelta(days=2)).isoformat(),
            "day1_sent": False,
            "day3_sent": False,
            "day7_sent": False,
        }
    ]
    users = [{"id": "user-1", "email": "u1@example.com", "unsubscribed_at": None}]
    fake_supabase = FakeSupabase(runs=runs, users=users)

    monkeypatch.setattr(email_service, "get_supabase_client", lambda: fake_supabase)

    def _raise_error(*, recipient_email: str, day: str, user_id: str) -> None:
        _ = (recipient_email, day, user_id)
        raise RuntimeError("provider down")

    monkeypatch.setattr(email_service, "send_followup_email", _raise_error)

    total = email_service.dispatch_followup_sequence()

    assert total == 0
    assert runs[0]["day1_sent"] is False


def test_mark_followup_sent_is_idempotent(monkeypatch) -> None:
    now = datetime.now(UTC)
    runs = [
        {
            "id": "run-1",
            "user_id": "user-1",
            "status": "completed",
            "completed_at": (now - timedelta(days=2)).isoformat(),
            "day1_sent": False,
            "day3_sent": False,
            "day7_sent": False,
        }
    ]
    users = [{"id": "user-1", "email": "u1@example.com", "unsubscribed_at": None}]
    fake_supabase = FakeSupabase(runs=runs, users=users)

    monkeypatch.setattr(email_service, "get_supabase_client", lambda: fake_supabase)

    first = email_service._mark_followup_sent(run_id="run-1", day_field="day1_sent")
    second = email_service._mark_followup_sent(run_id="run-1", day_field="day1_sent")

    assert first is True
    assert second is False
