from __future__ import annotations

import importlib
from datetime import UTC, datetime
from typing import Any

from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.core.database import get_supabase_client


class FakeResponse:
    def __init__(self, data: list[dict[str, Any]], count: int | None = None):
        self.data = data
        self.count = count


class FakeQuery:
    def __init__(self, supabase, table_name: str):
        self._supabase = supabase
        self._table_name = table_name
        self._operation = "select"
        self._select_fields = "*"
        self._filters: dict[str, Any] = {}
        self._order_field: str | None = None
        self._order_desc = False
        self._range_start: int | None = None
        self._range_end: int | None = None
        self._in_filters: dict[str, list[Any]] = {}

    def select(self, fields: str, count: str | None = None):
        self._operation = "select"
        self._select_fields = fields
        return self

    def eq(self, field: str, value: Any):
        self._filters[field] = value
        return self

    def order(self, field: str, desc: bool = False):
        self._order_field = field
        self._order_desc = desc
        return self

    def range(self, start: int, end: int):
        self._range_start = start
        self._range_end = end
        return self

    def in_(self, field: str, values: list[Any]):
        self._in_filters[field] = values
        return self

    def limit(self, _n: int):
        return self

    def execute(self):
        if self._table_name == "cost_tracking" and self._operation == "select":
            rows = [dict(row) for row in self._supabase.cost_rows]
            for field, value in self._filters.items():
                rows = [row for row in rows if row.get(field) == value]
            if self._range_start is not None and self._range_end is not None:
                rows = rows[self._range_start : self._range_end + 1]
            fields = [field.strip() for field in self._select_fields.split(",")]
            projected: list[dict[str, Any]] = []
            for row in rows:
                projected.append({field: row.get(field) for field in fields})
            return FakeResponse(projected, count=len(projected))

        if self._table_name == "users" and self._operation == "select":
            ids = self._in_filters.get("id", [])
            rows = [
                {"id": user_id, "email": self._supabase.users_by_id[user_id]}
                for user_id in ids
                if user_id in self._supabase.users_by_id
            ]
            return FakeResponse(rows)

        if self._table_name == "runs" and self._operation == "select":
            if (
                "error_code" in self._select_fields
                and not self._supabase.support_error_columns
            ):
                raise RuntimeError("column runs.error_code does not exist")

            rows = [dict(row) for row in self._supabase.run_rows]
            for field, value in self._filters.items():
                rows = [row for row in rows if row.get(field) == value]

            for field, values in self._in_filters.items():
                rows = [row for row in rows if row.get(field) in values]

            if self._order_field is not None:
                rows = sorted(
                    rows,
                    key=lambda row: str(row.get(self._order_field, "")),
                    reverse=self._order_desc,
                )

            total = len(rows)

            if self._range_start is not None and self._range_end is not None:
                rows = rows[self._range_start : self._range_end + 1]

            fields = [field.strip() for field in self._select_fields.split(",")]
            projected: list[dict[str, Any]] = []
            for row in rows:
                projected.append({field: row.get(field) for field in fields})

            return FakeResponse(projected, count=total)

        if self._table_name == "qualifier_responses" and self._operation == "select":
            rows = [dict(row) for row in self._supabase.qualifier_rows]
            for field, value in self._filters.items():
                rows = [row for row in rows if row.get(field) == value]

            if self._order_field is not None:
                rows = sorted(
                    rows,
                    key=lambda row: str(row.get(self._order_field, "")),
                    reverse=self._order_desc,
                )

            total = len(rows)

            if self._range_start is not None and self._range_end is not None:
                rows = rows[self._range_start : self._range_end + 1]

            fields = [field.strip() for field in self._select_fields.split(",")]
            projected: list[dict[str, Any]] = []
            for row in rows:
                projected.append({field: row.get(field) for field in fields})

            return FakeResponse(projected, count=total)

        return FakeResponse([])


class FakeSupabase:
    def __init__(self, *, support_error_columns: bool = True):
        self.support_error_columns = support_error_columns
        current_month = datetime.now(UTC).strftime("%Y-%m")
        self.cost_rows = [{"month": current_month, "total_usd": "12.34"}]
        self.users_by_id = {
            "user-1": "anna@example.com",
            "user-2": "bela@example.com",
            "user-3": "csilla@example.com",
        }
        self.run_rows = [
            {
                "id": "run-older",
                "user_id": "user-1",
                "topic": "Messaging",
                "audience": "SMB",
                "status": "completed",
                "persona_count": 18,
                "cost_usd": 1.15,
                "created_at": datetime(2026, 3, 20, 10, 0, tzinfo=UTC).isoformat(),
                "completed_at": datetime(2026, 3, 20, 10, 15, tzinfo=UTC).isoformat(),
            },
            {
                "id": "run-mid",
                "user_id": "user-2",
                "topic": "Pricing",
                "audience": "Mid-market",
                "status": "failed",
                "persona_count": 4,
                "cost_usd": 0.64,
                "created_at": datetime(2026, 3, 21, 8, 0, tzinfo=UTC).isoformat(),
                "completed_at": datetime(2026, 3, 21, 8, 6, tzinfo=UTC).isoformat(),
                "error_code": "PERSONA_TIMEOUT",
                "error_at": datetime(2026, 3, 21, 8, 5, tzinfo=UTC).isoformat(),
            },
            {
                "id": "run-new",
                "user_id": "user-3",
                "topic": "Positioning",
                "audience": "Enterprise",
                "status": "partial",
                "persona_count": 13,
                "cost_usd": 0.92,
                "created_at": datetime(2026, 3, 22, 9, 0, tzinfo=UTC).isoformat(),
                "completed_at": datetime(2026, 3, 22, 9, 9, tzinfo=UTC).isoformat(),
            },
        ]
        self.qualifier_rows = [
            {
                "id": "qr-older",
                "run_id": "run-older",
                "user_id": "user-1",
                "role_answer": "founder_ceo",
                "use_case_answer": "message_validation",
                "created_at": datetime(2026, 3, 20, 10, 1, tzinfo=UTC).isoformat(),
            },
            {
                "id": "qr-new",
                "run_id": "run-new",
                "user_id": "user-3",
                "role_answer": "growth_marketer",
                "use_case_answer": "persona_research",
                "created_at": datetime(2026, 3, 22, 9, 1, tzinfo=UTC).isoformat(),
            },
            {
                "id": "qr-orphan",
                "run_id": "run-missing",
                "user_id": "user-missing",
                "role_answer": "other",
                "use_case_answer": "other",
                "created_at": datetime(2026, 3, 23, 9, 1, tzinfo=UTC).isoformat(),
            },
        ]

    def table(self, name: str):
        return FakeQuery(self, name)


def build_client(monkeypatch, fake_supabase: FakeSupabase | None = None) -> TestClient:
    if fake_supabase is None:
        fake_supabase = FakeSupabase()

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
    import app.routers.operator as operator_router

    importlib.reload(operator_router)
    importlib.reload(main)

    monkeypatch.setattr(operator_router, "get_supabase_client", lambda: fake_supabase)

    return TestClient(main.app)


def test_send_followups_requires_valid_bearer(monkeypatch):
    client = build_client(monkeypatch)

    response = client.post("/api/v1/operator/send-followups")
    assert response.status_code == 403

    response = client.post(
        "/api/v1/operator/send-followups",
        headers={"Authorization": "Bearer wrong-key"},
    )
    assert response.status_code == 403


def test_send_followups_returns_sent_count(monkeypatch):
    client = build_client(monkeypatch)

    import app.routers.operator as operator_router

    monkeypatch.setattr(operator_router, "dispatch_followup_sequence", lambda: 3)

    response = client.post(
        "/api/v1/operator/send-followups",
        headers={"Authorization": "Bearer operator-key"},
    )

    assert response.status_code == 200
    assert response.json() == {"sent": 3}


def test_list_runs_requires_valid_bearer(monkeypatch):
    client = build_client(monkeypatch)

    response = client.get("/api/v1/operator/runs")
    assert response.status_code == 403

    response = client.get(
        "/api/v1/operator/runs",
        headers={"Authorization": "Bearer wrong-key"},
    )
    assert response.status_code == 403


def test_list_runs_returns_paginated_rows_in_desc_order(monkeypatch):
    client = build_client(monkeypatch)

    response = client.get(
        "/api/v1/operator/runs?page=1&page_size=2",
        headers={"Authorization": "Bearer operator-key"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["page"] == 1
    assert payload["page_size"] == 2
    assert payload["total"] == 3
    assert [item["run_id"] for item in payload["items"]] == ["run-new", "run-mid"]
    assert payload["items"][0]["user_email"] == "csilla@example.com"


def test_list_runs_filters_failed_and_includes_error_metadata(monkeypatch):
    client = build_client(monkeypatch)

    response = client.get(
        "/api/v1/operator/runs?status=failed",
        headers={"Authorization": "Bearer operator-key"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 1
    assert payload["items"][0]["status"] == "failed"
    assert payload["items"][0]["error_code"] == "PERSONA_TIMEOUT"
    assert isinstance(payload["items"][0]["error_at"], str)


def test_failed_and_partial_runs_always_have_error_metadata(monkeypatch):
    fake_supabase = FakeSupabase(support_error_columns=False)
    client = build_client(monkeypatch, fake_supabase=fake_supabase)

    response = client.get(
        "/api/v1/operator/runs?page=1&page_size=10",
        headers={"Authorization": "Bearer operator-key"},
    )

    assert response.status_code == 200
    items = response.json()["items"]
    by_id = {item["run_id"]: item for item in items}
    assert by_id["run-mid"]["error_code"] == "RUN_FAILED"
    assert isinstance(by_id["run-mid"]["error_at"], str)
    assert by_id["run-new"]["error_code"] == "RUN_PARTIAL"
    assert isinstance(by_id["run-new"]["error_at"], str)


def test_pagination_bounds_max_page_size_and_empty_page(monkeypatch):
    client = build_client(monkeypatch)

    response = client.get(
        "/api/v1/operator/runs?page_size=101",
        headers={"Authorization": "Bearer operator-key"},
    )
    assert response.status_code == 422

    response = client.get(
        "/api/v1/operator/runs?page=3&page_size=2",
        headers={"Authorization": "Bearer operator-key"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["page"] == 3
    assert payload["items"] == []


def test_list_qualifier_responses_requires_valid_bearer(monkeypatch):
    client = build_client(monkeypatch)

    response = client.get("/api/v1/operator/qualifier-responses")
    assert response.status_code == 403

    response = client.get(
        "/api/v1/operator/qualifier-responses",
        headers={"Authorization": "Bearer wrong-key"},
    )
    assert response.status_code == 403


def test_list_qualifier_responses_returns_desc_items_with_expected_fields(monkeypatch):
    client = build_client(monkeypatch)

    response = client.get(
        "/api/v1/operator/qualifier-responses?page=1&page_size=10",
        headers={"Authorization": "Bearer operator-key"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["page"] == 1
    assert payload["page_size"] == 10
    assert payload["total"] == 2

    items = payload["items"]
    assert [item["user_email"] for item in items] == [
        "csilla@example.com",
        "anna@example.com",
    ]
    assert [item["created_at"] for item in items] == sorted(
        [item["created_at"] for item in items], reverse=True
    )
    assert set(items[0].keys()) == {
        "user_email",
        "role_answer",
        "use_case_answer",
        "created_at",
    }


def test_list_qualifier_responses_total_is_global_not_page_local(monkeypatch):
    client = build_client(monkeypatch)

    response = client.get(
        "/api/v1/operator/qualifier-responses?page=1&page_size=1",
        headers={"Authorization": "Bearer operator-key"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 2
    assert len(payload["items"]) == 1
    assert payload["items"][0]["user_email"] == "csilla@example.com"


def test_list_qualifier_responses_enforces_run_user_link(monkeypatch):
    fake_supabase = FakeSupabase()
    fake_supabase.qualifier_rows.insert(
        0,
        {
            "id": "qr-mismatch",
            "run_id": "run-new",
            "user_id": "user-1",
            "role_answer": "founder_ceo",
            "use_case_answer": "message_validation",
            "created_at": datetime(2026, 3, 24, 9, 1, tzinfo=UTC).isoformat(),
        },
    )
    client = build_client(monkeypatch, fake_supabase=fake_supabase)

    response = client.get(
        "/api/v1/operator/qualifier-responses?page=1&page_size=10",
        headers={"Authorization": "Bearer operator-key"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 2
    assert [item["user_email"] for item in payload["items"]] == [
        "csilla@example.com",
        "anna@example.com",
    ]


def test_list_qualifier_responses_skips_invalid_text_rows(monkeypatch):
    fake_supabase = FakeSupabase()
    fake_supabase.qualifier_rows[1]["role_answer"] = "x" * 501
    client = build_client(monkeypatch, fake_supabase=fake_supabase)

    response = client.get(
        "/api/v1/operator/qualifier-responses?page=1&page_size=10",
        headers={"Authorization": "Bearer operator-key"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 1
    assert [item["user_email"] for item in payload["items"]] == ["anna@example.com"]


def test_get_cost_returns_ok_payload_below_80_percent(monkeypatch):
    fake_supabase = FakeSupabase()
    current_month = datetime.now(UTC).strftime("%Y-%m")
    fake_supabase.cost_rows = [{"month": current_month, "total_usd": "12.34"}]
    client = build_client(monkeypatch, fake_supabase=fake_supabase)

    response = client.get(
        "/api/v1/operator/cost",
        headers={"Authorization": "Bearer operator-key"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["month"] == current_month
    assert payload["total_usd"] == 12.34
    assert payload["cap_usd"] == 50.0
    assert abs(payload["percentage"] - 24.68) < 0.01
    assert payload["status"] == "ok"


def test_get_cost_returns_ok_for_zero_spend(monkeypatch):
    fake_supabase = FakeSupabase()
    current_month = datetime.now(UTC).strftime("%Y-%m")
    fake_supabase.cost_rows = []
    client = build_client(monkeypatch, fake_supabase=fake_supabase)

    response = client.get(
        "/api/v1/operator/cost",
        headers={"Authorization": "Bearer operator-key"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["total_usd"] == 0.0
    assert payload["percentage"] == 0.0
    assert payload["status"] == "ok"


def test_get_cost_requires_valid_bearer(monkeypatch):
    client = build_client(monkeypatch)

    response = client.get("/api/v1/operator/cost")
    assert response.status_code == 403

    response = client.get(
        "/api/v1/operator/cost",
        headers={"Authorization": "Bearer wrong-key"},
    )
    assert response.status_code == 403


def test_get_cost_returns_warning_payload_at_80_percent(monkeypatch):
    fake_supabase = FakeSupabase()
    current_month = datetime.now(UTC).strftime("%Y-%m")
    fake_supabase.cost_rows = [{"month": current_month, "total_usd": "40.00"}]
    client = build_client(monkeypatch, fake_supabase=fake_supabase)

    response = client.get(
        "/api/v1/operator/cost",
        headers={"Authorization": "Bearer operator-key"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "month": current_month,
        "total_usd": 40.0,
        "cap_usd": 50.0,
        "percentage": 80.0,
        "status": "warning",
    }


def test_get_cost_returns_capped_payload_at_or_above_100_percent(monkeypatch):
    fake_supabase = FakeSupabase()
    current_month = datetime.now(UTC).strftime("%Y-%m")
    fake_supabase.cost_rows = [{"month": current_month, "total_usd": "50.00"}]
    client = build_client(monkeypatch, fake_supabase=fake_supabase)

    response = client.get(
        "/api/v1/operator/cost",
        headers={"Authorization": "Bearer operator-key"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["month"] == current_month
    assert payload["total_usd"] == 50.0
    assert payload["cap_usd"] == 50.0
    assert payload["percentage"] == 100.0
    assert payload["status"] == "capped"
