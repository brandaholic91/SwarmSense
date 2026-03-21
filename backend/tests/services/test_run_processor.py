from __future__ import annotations

import asyncio
import importlib
from datetime import UTC, datetime

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
        self._payload: dict[str, object] | None = None
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

    def insert(self, payload: dict[str, object]):
        self._operation = "insert"
        self._payload = payload
        return self

    def update(self, payload: dict[str, object]):
        self._operation = "update"
        self._payload = payload
        return self

    def execute(self):
        if self._table_name == "cost_tracking" and self._operation == "select":
            return FakeResponse(self._supabase.cost_rows)

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
            }
            self._supabase.inserted_runs.append(row)
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
            self._supabase.updates.append(
                {
                    "run_id": self._eq_value,
                    "payload": dict(self._payload),
                }
            )
            return FakeResponse([{"id": self._eq_value, **self._payload}])

        return FakeResponse([])


class FakeSupabase:
    def __init__(self, total_usd: str | None = "1.00"):
        self.cost_rows = [] if total_usd is None else [{"total_usd": total_usd}]
        self.inserted_runs: list[dict[str, object]] = []
        self.inserted_qualifiers: list[dict[str, object]] = []
        self.updates: list[dict[str, object]] = []

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


def test_process_run_fails_when_successful_personas_below_threshold(
    monkeypatch,
) -> None:
    _seed_env(monkeypatch)
    fake_supabase = FakeSupabase()

    import app.services.run_processor as run_processor

    monkeypatch.setattr(run_processor, "get_supabase_client", lambda: fake_supabase)

    async def fake_engine(*, topic: str, audience: str):
        _ = (topic, audience)
        return PersonaRunResult(
            total_personas=15,
            successful_count=11,
            responses=[],
            failures=[
                PersonaFailure(
                    persona_name="Persona 1",
                    error_code="OPENROUTER_RATE_LIMIT",
                    error_message="rate limit",
                )
            ],
            handoff_payload=[],
        )

    captured_sentry: list[str] = []

    monkeypatch.setattr(run_processor, "execute_persona_engine", fake_engine)
    monkeypatch.setattr(
        run_processor.sentry_sdk,
        "capture_message",
        lambda msg, level=None: captured_sentry.append(msg),
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
    assert captured_sentry


def test_process_run_moves_to_composing_when_threshold_met(monkeypatch) -> None:
    _seed_env(monkeypatch)
    fake_supabase = FakeSupabase()

    import app.services.run_processor as run_processor

    monkeypatch.setattr(run_processor, "get_supabase_client", lambda: fake_supabase)

    async def fake_engine(*, topic: str, audience: str):
        _ = (topic, audience)
        responses = [
            PersonaResponse(
                name=f"Persona-{idx}",
                role="Role",
                stance="support",
                primary_argument="Erv",
                change_condition="Feltetel",
            )
            for idx in range(MIN_SUCCESSFUL_PERSONAS)
        ]
        return PersonaRunResult(
            total_personas=15,
            successful_count=MIN_SUCCESSFUL_PERSONAS,
            responses=responses,
            failures=[],
            handoff_payload=[item.model_dump() for item in responses],
        )

    monkeypatch.setattr(run_processor, "execute_persona_engine", fake_engine)

    result = asyncio.run(
        process_run(
            run_id="run-1",
            user_id="user-1",
            topic="Tema",
            audience="Kozonseg",
        )
    )

    assert result.successful_count == MIN_SUCCESSFUL_PERSONAS
    assert fake_supabase.updates[0]["payload"]["status"] == "running"
    assert fake_supabase.updates[1]["payload"]["status"] == "composing"


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
