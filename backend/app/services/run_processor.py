from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from typing import Any

import sentry_sdk

from app.core.database import get_supabase_client
from app.services.persona_engine import PersonaRunResult, execute_persona_engine

MIN_SUCCESSFUL_PERSONAS = 12


async def process_run(
    *,
    run_id: str,
    user_id: str,
    topic: str,
    audience: str,
) -> PersonaRunResult:
    _ = user_id
    _update_run_row(run_id=run_id, payload={"status": "running"})

    result = await execute_persona_engine(topic=topic, audience=audience)
    if result.successful_count < MIN_SUCCESSFUL_PERSONAS:
        failure_timestamp = datetime.now(UTC).isoformat()
        _update_run_row(
            run_id=run_id,
            payload={
                "status": "failed",
                "persona_count": result.successful_count,
                "completed_at": failure_timestamp,
            },
        )
        _capture_failed_run(
            run_id=run_id,
            error_code="PERSONA_SUCCESS_THRESHOLD_NOT_MET",
            timestamp=failure_timestamp,
            successful_count=result.successful_count,
            required_count=MIN_SUCCESSFUL_PERSONAS,
        )
        return result

    _update_run_row(
        run_id=run_id,
        payload={
            "status": "composing",
            "persona_count": result.successful_count,
        },
    )
    return result


def _update_run_row(*, run_id: str, payload: dict[str, Any]) -> None:
    supabase = get_supabase_client()
    supabase.table("runs").update(payload).eq("id", run_id).execute()


def _capture_failed_run(
    *,
    run_id: str,
    error_code: str,
    timestamp: str,
    successful_count: int,
    required_count: int,
) -> None:
    with sentry_sdk.push_scope() as scope:
        scope.set_tag("run_id", run_id)
        scope.set_tag("error_code", error_code)
        scope.set_extra("timestamp", timestamp)
        scope.set_extra("successful_count", successful_count)
        scope.set_extra("required_count", required_count)
        sentry_sdk.capture_exception(
            RuntimeError(
                "Persona processing failed: successful personas below required threshold."
            )
        )


def dispatch_run_processing(
    *,
    run_id: str,
    user_id: str,
    topic: str,
    audience: str,
) -> None:
    try:
        asyncio.run(
            process_run(
                run_id=run_id,
                user_id=user_id,
                topic=topic,
                audience=audience,
            )
        )
    except Exception as exc:  # pragma: no cover - defensive background fallback
        failure_timestamp = datetime.now(UTC).isoformat()
        try:
            _update_run_row(
                run_id=run_id,
                payload={
                    "status": "failed",
                    "completed_at": failure_timestamp,
                },
            )
        except Exception:
            pass
        with sentry_sdk.push_scope() as scope:
            scope.set_tag("run_id", run_id)
            scope.set_tag("error_code", "RUN_PROCESSING_UNHANDLED")
            scope.set_extra("timestamp", failure_timestamp)
            sentry_sdk.capture_exception(exc)
