from __future__ import annotations

import asyncio
import importlib
from datetime import UTC, date, datetime
from typing import Any

from fastapi.testclient import TestClient

from app.core import cost_enforcement
from app.core.config import get_settings
from app.core.database import get_supabase_client
from app.models.persona import PersonaFailure, PersonaResponse, PersonaRunResult
from app.services.run_processor import MIN_SUCCESSFUL_PERSONAS, process_run

TEST_INTERNAL_SECRET = "test-internal-secret"
INTERNAL_SECRET_HEADER = {"X-Internal-Secret": TEST_INTERNAL_SECRET}


class FakeResponse:
    def __init__(self, data):
        self.data = data


class FakeQuery:
    def __init__(self, supabase, table_name: str):
        self._supabase = supabase
        self._table_name = table_name
        self._payload: dict[str, Any] | None = None
        self._operation = "select"
        self._eq_value: str | None = None

    def select(self, _fields: str):
        self._operation = "select"
        return self

    def eq(self, _field: str, value: object):
        if isinstance(value, str):
            self._eq_value = value
        return self

    def limit(self, _n: int):
        return self

    def insert(self, payload: dict[str, Any]):
        self._operation = "insert"
        self._payload = payload
        return self

    def update(self, payload: dict[str, Any]):
        self._operation = "update"
        self._payload = payload
        return self

    def execute(self):
        if self._table_name == "cost_tracking" and self._operation == "select":
            if self._eq_value is None:
                return FakeResponse(self._supabase.cost_rows)
            rows = [
                row
                for row in self._supabase.cost_rows
                if row.get("month") == self._eq_value
            ]
            return FakeResponse(rows)

        if self._table_name == "cost_tracking" and self._operation == "insert":
            assert self._payload is not None
            self._supabase.cost_rows.append(dict(self._payload))
            return FakeResponse([dict(self._payload)])

        if self._table_name == "cost_tracking" and self._operation == "update":
            assert self._payload is not None
            for row in self._supabase.cost_rows:
                if row.get("month") == self._eq_value:
                    row.update(self._payload)
            return FakeResponse(self._supabase.cost_rows)

        if self._table_name == "users" and self._operation == "select":
            if self._eq_value is None:
                return FakeResponse([])
            email = self._supabase.users_by_id.get(self._eq_value)
            if email is None:
                return FakeResponse([])
            return FakeResponse([{"email": email}])

        if self._table_name == "runs" and self._operation == "select":
            if self._eq_value is None:
                return FakeResponse([])
            row = self._supabase.run_rows.get(self._eq_value)
            if row is None:
                return FakeResponse([])
            return FakeResponse([dict(row)])

        if self._table_name == "runs" and self._operation == "insert":
            assert self._payload is not None
            run_id = f"run-{len(self._supabase.inserted_runs) + 1}"
            row = {
                "id": run_id,
                "user_id": self._payload["user_id"],
                "topic": self._payload["topic"],
                "audience": self._payload["audience"],
                "status": self._payload["status"],
                "created_at": datetime.now(UTC).isoformat(),
                "persona_count": None,
                "completed_at": None,
                "cost_usd": None,
            }
            self._supabase.inserted_runs.append(row)
            self._supabase.run_rows[run_id] = dict(row)
            return FakeResponse([row])

        if self._table_name == "qualifier_responses" and self._operation == "insert":
            assert self._payload is not None
            row = {
                "id": f"qualifier-{len(self._supabase.inserted_qualifiers) + 1}",
                "run_id": self._payload["run_id"],
                "user_id": self._payload["user_id"],
                "role_answer": self._payload["role_answer"],
                "use_case_answer": self._payload["use_case_answer"],
                "created_at": datetime.now(UTC).isoformat(),
            }
            self._supabase.inserted_qualifiers.append(row)
            return FakeResponse([row])

        if self._table_name == "runs" and self._operation == "update":
            assert self._payload is not None
            run_id = self._eq_value
            self._supabase.updates.append(
                {
                    "run_id": run_id,
                    "payload": dict(self._payload),
                }
            )
            if run_id and run_id in self._supabase.run_rows:
                self._supabase.run_rows[run_id].update(self._payload)
            return FakeResponse([{"id": run_id, **self._payload}])

        return FakeResponse([])


class FakeSupabase:
    def __init__(self, total_usd: str | None = "1.00"):
        current_month = date.today().strftime("%Y-%m")
        self.cost_rows = (
            []
            if total_usd is None
            else [{"month": current_month, "total_usd": total_usd}]
        )
        self.users_by_id: dict[str, str] = {"user-1": "test@example.com"}
        self.run_rows: dict[str, dict[str, Any]] = {
            "run-1": {
                "id": "run-1",
                "status": "queued",
                "cost_usd": None,
                "persona_count": None,
                "completed_at": None,
            }
        }
        self.inserted_runs: list[dict[str, Any]] = []
        self.inserted_qualifiers: list[dict[str, Any]] = []
        self.updates: list[dict[str, Any]] = []

    def table(self, name: str):
        return FakeQuery(self, name)


def _seed_env(monkeypatch) -> None:
    monkeypatch.setenv("SWARMSENSE_SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setenv("SWARMSENSE_SUPABASE_SERVICE_KEY", "service-key")
    monkeypatch.setenv("SWARMSENSE_KIMI_API_KEY", "kimi-key")
    monkeypatch.setenv("SWARMSENSE_OPERATOR_API_KEY", "operator-key")
    monkeypatch.setenv("SWARMSENSE_INTERNAL_SECRET", TEST_INTERNAL_SECRET)
    monkeypatch.setenv("SWARMSENSE_ENVIRONMENT", "development")
    monkeypatch.setenv("SWARMSENSE_FRONTEND_ORIGIN", "https://swarmsense.vercel.app")
    monkeypatch.setenv("SWARMSENSE_RESEND_API_KEY", "re_test")
    monkeypatch.setenv("SWARMSENSE_OPENROUTER_API_KEY", "or_test")
    get_settings.cache_clear()
    get_supabase_client.cache_clear()


def _build_result(
    *, successful_count: int, total_personas: int, cost_usd: float
) -> PersonaRunResult:
    responses = [
        PersonaResponse(
            name=f"Persona-{idx}",
            role="Role",
            stance="support" if idx % 2 == 0 else "conditional",
            primary_argument=f"Erv-{idx % 3}",
            change_condition="Feltetel",
        )
        for idx in range(successful_count)
    ]
    failures = [
        PersonaFailure(
            persona_name=f"Missing-{idx}",
            error_code="OPENROUTER_UPSTREAM_ERROR",
            error_message="failed",
        )
        for idx in range(total_personas - successful_count)
    ]
    return PersonaRunResult(
        total_personas=total_personas,
        successful_count=successful_count,
        responses=responses,
        failures=failures,
        handoff_payload=[item.model_dump() for item in responses],
        cost_usd=cost_usd,
    )


def _patch_fake_engine(monkeypatch, run_processor, result: PersonaRunResult) -> None:
    async def fake_engine(*, topic: str, audience: str):
        _ = (topic, audience)
        return result

    monkeypatch.setattr(run_processor, "execute_persona_engine", fake_engine)


def test_process_run_marks_partial_and_dispatches_email(monkeypatch) -> None:
    _seed_env(monkeypatch)
    fake_supabase = FakeSupabase("1.00")

    import app.services.run_processor as run_processor

    monkeypatch.setattr(run_processor, "get_supabase_client", lambda: fake_supabase)
    _patch_fake_engine(
        monkeypatch,
        run_processor,
        _build_result(successful_count=12, total_personas=15, cost_usd=0.25),
    )

    email_calls: list[dict[str, Any]] = []
    monkeypatch.setattr(
        run_processor,
        "send_run_result_email",
        lambda *, recipient_email, result_payload: email_calls.append(
            {"recipient_email": recipient_email, "result_payload": result_payload}
        ),
    )

    asyncio.run(
        process_run(
            run_id="run-1",
            user_id="user-1",
            topic="Tema",
            audience="Kozonseg",
        )
    )

    assert fake_supabase.updates[0]["payload"]["status"] == "running"
    assert fake_supabase.updates[1]["payload"]["status"] == "composing"
    assert fake_supabase.updates[2]["payload"]["status"] == "partial"
    assert fake_supabase.updates[2]["payload"]["persona_count"] == 12
    assert fake_supabase.updates[2]["payload"]["cost_usd"] == "0.25"
    assert isinstance(fake_supabase.updates[2]["payload"]["completed_at"], str)
    assert email_calls[0]["recipient_email"] == "test@example.com"
    assert email_calls[0]["result_payload"]["persona_count_label"] == "12/15 persona"
    assert fake_supabase.cost_rows[0]["total_usd"] == "1.25"


def test_process_run_marks_completed_and_dispatches_email(monkeypatch) -> None:
    _seed_env(monkeypatch)
    fake_supabase = FakeSupabase("2.00")

    import app.services.run_processor as run_processor

    monkeypatch.setattr(run_processor, "get_supabase_client", lambda: fake_supabase)
    _patch_fake_engine(
        monkeypatch,
        run_processor,
        _build_result(successful_count=15, total_personas=15, cost_usd=0.30),
    )

    email_calls: list[dict[str, Any]] = []
    monkeypatch.setattr(
        run_processor,
        "send_run_result_email",
        lambda *, recipient_email, result_payload: email_calls.append(
            {"recipient_email": recipient_email, "result_payload": result_payload}
        ),
    )

    asyncio.run(
        process_run(
            run_id="run-1",
            user_id="user-1",
            topic="Tema",
            audience="Kozonseg",
        )
    )

    assert fake_supabase.updates[2]["payload"]["status"] == "completed"
    assert fake_supabase.updates[2]["payload"]["persona_count"] == 15
    assert fake_supabase.updates[2]["payload"]["cost_usd"] == "0.3"
    assert email_calls[0]["result_payload"]["persona_count_label"] == "15/15 persona"
    assert fake_supabase.cost_rows[0]["total_usd"] == "2.30"


def test_process_run_fails_when_successful_personas_below_threshold(
    monkeypatch,
) -> None:
    _seed_env(monkeypatch)
    fake_supabase = FakeSupabase("1.00")

    import app.services.run_processor as run_processor

    monkeypatch.setattr(run_processor, "get_supabase_client", lambda: fake_supabase)
    _patch_fake_engine(
        monkeypatch,
        run_processor,
        _build_result(successful_count=11, total_personas=15, cost_usd=0.15),
    )

    captured_sentry: list[str] = []
    monkeypatch.setattr(
        run_processor.sentry_sdk,
        "capture_message",
        lambda msg, level=None: captured_sentry.append(msg),
    )

    email_calls: list[dict[str, Any]] = []
    monkeypatch.setattr(
        run_processor,
        "send_run_result_email",
        lambda *, recipient_email, result_payload: email_calls.append(
            {"recipient_email": recipient_email, "result_payload": result_payload}
        ),
    )

    result = asyncio.run(
        process_run(
            run_id="run-1",
            user_id="user-1",
            topic="Tema",
            audience="Kozonseg",
        )
    )

    assert result.successful_count == 11
    assert fake_supabase.updates[0]["payload"]["status"] == "running"
    assert fake_supabase.updates[1]["payload"]["status"] == "failed"
    assert fake_supabase.updates[1]["payload"]["persona_count"] == 11
    assert fake_supabase.updates[1]["payload"]["cost_usd"] == "0.15"
    assert isinstance(fake_supabase.updates[1]["payload"]["completed_at"], str)
    assert captured_sentry
    assert not email_calls
    assert fake_supabase.cost_rows[0]["total_usd"] == "1.15"


def test_monthly_cost_tracking_creates_missing_month_row(monkeypatch) -> None:
    _seed_env(monkeypatch)
    fake_supabase = FakeSupabase(total_usd=None)

    import app.services.run_processor as run_processor

    monkeypatch.setattr(run_processor, "get_supabase_client", lambda: fake_supabase)
    _patch_fake_engine(
        monkeypatch,
        run_processor,
        _build_result(successful_count=15, total_personas=15, cost_usd=0.42),
    )
    monkeypatch.setattr(
        run_processor,
        "send_run_result_email",
        lambda *, recipient_email, result_payload: None,
    )

    asyncio.run(
        process_run(
            run_id="run-1",
            user_id="user-1",
            topic="Tema",
            audience="Kozonseg",
        )
    )

    assert len(fake_supabase.cost_rows) == 1
    assert fake_supabase.cost_rows[0]["month"] == date.today().strftime("%Y-%m")
    assert fake_supabase.cost_rows[0]["total_usd"] == "0.42"


def test_runs_endpoint_dispatches_into_real_run_processor(monkeypatch) -> None:
    _seed_env(monkeypatch)
    fake_supabase = FakeSupabase("1.00")

    import app.main as main
    import app.routers.runs as runs_router
    import app.services.run_processor as run_processor

    importlib.reload(run_processor)
    importlib.reload(runs_router)
    importlib.reload(main)

    monkeypatch.setattr(cost_enforcement, "get_supabase_client", lambda: fake_supabase)
    monkeypatch.setattr(runs_router, "get_supabase_client", lambda: fake_supabase)
    monkeypatch.setattr(run_processor, "get_supabase_client", lambda: fake_supabase)

    captured: list[dict[str, str]] = []

    async def fake_process_run(*, run_id: str, user_id: str, topic: str, audience: str):
        captured.append(
            {
                "run_id": run_id,
                "user_id": user_id,
                "topic": topic,
                "audience": audience,
            }
        )
        return PersonaRunResult(
            total_personas=15,
            successful_count=MIN_SUCCESSFUL_PERSONAS,
            responses=[],
            failures=[],
            handoff_payload=[],
            cost_usd=0.0,
        )

    monkeypatch.setattr(run_processor, "process_run", fake_process_run)

    client = TestClient(main.app)
    response = client.post(
        "/api/v1/runs",
        json={"user_id": "user-1", "topic": "Pricing", "audience": "SMB CFO"},
        headers=INTERNAL_SECRET_HEADER,
    )

    assert response.status_code == 200
    assert captured == [
        {
            "run_id": "run-1",
            "user_id": "user-1",
            "topic": "Pricing",
            "audience": "SMB CFO",
        }
    ]
