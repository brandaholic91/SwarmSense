from __future__ import annotations

import asyncio
from datetime import UTC, date, datetime
from decimal import Decimal, InvalidOperation
from typing import Any

import sentry_sdk

from app.core.database import get_supabase_client
from app.models.persona import SynthesisResult
from app.services.email_service import send_run_result_email
from app.services.persona_engine import PersonaRunResult, execute_persona_engine
from app.services.synthesis_service import execute_synthesis

MIN_SUCCESSFUL_PERSONAS = 12
CONSENSUS_THRESHOLD = 15
FINAL_STATUSES = {"completed", "partial", "failed"}


async def process_run(
    *,
    run_id: str,
    user_id: str,
    topic: str,
    audience: str,
) -> PersonaRunResult:
    _update_run_row(run_id=run_id, payload={"status": "running", "persona_count": 0})

    def on_persona_completed(processed_count: int, total_personas: int) -> None:
        _ = total_personas
        _update_run_row(
            run_id=run_id,
            payload={"status": "running", "persona_count": processed_count},
        )

    try:
        result = await execute_persona_engine(
            topic=topic,
            audience=audience,
            on_persona_completed=on_persona_completed,
        )
    except Exception as exc:
        failure_timestamp = datetime.now(UTC).isoformat()
        final_cost = Decimal("0")
        should_increment = _should_increment_monthly_cost(
            run_id=run_id
        )  # P1: check right before write
        _update_run_row(
            run_id=run_id,
            payload={
                "status": "failed",
                "completed_at": failure_timestamp,
                "cost_usd": str(final_cost),
            },
        )
        _increment_monthly_cost(
            run_id=run_id,
            run_cost=final_cost,
            should_increment=should_increment,
        )
        with sentry_sdk.push_scope() as scope:
            scope.set_tag("run_id", run_id)
            scope.set_tag("error_code", "PERSONA_ENGINE_UNHANDLED")
            scope.set_extra("timestamp", failure_timestamp)
            sentry_sdk.capture_exception(exc)
        raise

    final_cost = _normalize_cost(result.cost_usd)
    completed_timestamp = datetime.now(UTC).isoformat()

    if result.successful_count < MIN_SUCCESSFUL_PERSONAS:
        should_increment = _should_increment_monthly_cost(run_id=run_id)  # P1
        _update_run_row(
            run_id=run_id,
            payload={
                "status": "failed",
                "persona_count": result.successful_count,
                "completed_at": completed_timestamp,
                "cost_usd": str(final_cost),
            },
        )
        _increment_monthly_cost(
            run_id=run_id,
            run_cost=final_cost,
            should_increment=should_increment,
        )
        _capture_failed_run(
            run_id=run_id,
            error_code="PERSONA_SUCCESS_THRESHOLD_NOT_MET",
            timestamp=completed_timestamp,
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

    synthesis: SynthesisResult | None = None
    try:
        synthesis = await execute_synthesis(
            personas=result.responses,
            topic=topic,
            audience=audience,
        )
    except Exception as exc:
        with sentry_sdk.push_scope() as scope:
            scope.set_tag("run_id", run_id)
            scope.set_tag("error_code", "SYNTHESIS_FAILED")
            sentry_sdk.capture_exception(exc)

    try:  # P9: catch aggregation/finalization errors to avoid stuck composing state
        final_status = _resolve_final_status(result=result)
        aggregation_payload = _build_result_payload(
            run_id=run_id,
            result=result,
            final_status=final_status,
            topic=topic,
            audience=audience,
            synthesis=synthesis,
        )
        should_increment = _should_increment_monthly_cost(run_id=run_id)  # P1
        _update_run_row(
            run_id=run_id,
            payload={
                "status": final_status,
                "persona_count": result.successful_count,
                "completed_at": completed_timestamp,
                "cost_usd": str(final_cost),
            },
        )
        _increment_monthly_cost(
            run_id=run_id,
            run_cost=final_cost,
            should_increment=should_increment,
        )
        if final_status in {"partial", "completed"}:
            _dispatch_result_email(
                run_id=run_id,
                user_id=user_id,
                payload=aggregation_payload,
            )
    except Exception as exc:
        should_increment = _should_increment_monthly_cost(run_id=run_id)
        _update_run_row(
            run_id=run_id,
            payload={
                "status": "failed",
                "completed_at": completed_timestamp,
                "cost_usd": str(final_cost),
            },
        )
        _increment_monthly_cost(
            run_id=run_id,
            run_cost=final_cost,
            should_increment=should_increment,
        )
        with sentry_sdk.push_scope() as scope:
            scope.set_tag("run_id", run_id)
            scope.set_tag("error_code", "RUN_FINALIZATION_UNHANDLED")
            scope.set_extra("completed_timestamp", completed_timestamp)
            sentry_sdk.capture_exception(exc)
        raise

    return result


def _resolve_final_status(
    *, result: PersonaRunResult
) -> str:  # P3: dead "failed" branch removed
    if result.successful_count < result.total_personas:
        return "partial"
    return "completed"


def _build_result_payload(
    *,
    run_id: str,
    result: PersonaRunResult,
    final_status: str,  # P12: status passed in, not recomputed
    topic: str,
    audience: str,
    synthesis: SynthesisResult | None,
) -> dict[str, Any]:
    stance_counts: dict[str, int] = {"support": 0, "reject": 0, "conditional": 0}
    arguments_frequency: dict[str, int] = {}

    for response in result.responses:
        stance_counts[response.stance] += 1
        argument = response.primary_argument.strip()
        if argument:
            arguments_frequency[argument] = arguments_frequency.get(argument, 0) + 1

    # handoff_payload already contains blueprint attributes (risk_appetite, etc.)
    personas_for_email: list[dict[str, Any]] = result.handoff_payload

    top_arguments = [
        argument
        for argument, _ in sorted(
            arguments_frequency.items(), key=lambda item: (-item[1], item[0])
        )[:3]
    ]

    aggregate_score_payload = _build_aggregate_score_payload(
        stance_counts=stance_counts
    )
    consensus_payload = _build_consensus_payload(stance_counts=stance_counts)

    return {
        "run_id": run_id,
        "status": final_status,
        "topic": topic,
        "audience": audience,
        "completed_persona_count": result.successful_count,
        "total_persona_count": result.total_personas,
        "persona_count_label": _format_persona_count_label(
            completed=result.successful_count,
            total=result.total_personas,
        ),
        "persona_count_header_display": _format_persona_count_header_display(
            completed=result.successful_count,
            total=result.total_personas,
            final_status=final_status,
        ),
        "stance_counts": stance_counts,
        "aggregate_score": aggregate_score_payload,
        "aggregate_score_display": aggregate_score_payload["display"],
        "consensus_flag": consensus_payload,
        "consensus_flag_display": consensus_payload["display"],
        "top_arguments": top_arguments,
        "personas": personas_for_email,
        "synthesis": synthesis.model_dump() if synthesis is not None else None,
    }


def _build_aggregate_score_payload(*, stance_counts: dict[str, int]) -> dict[str, Any]:
    support_count = stance_counts.get("support", 0)
    reject_count = stance_counts.get("reject", 0)
    conditional_count = stance_counts.get("conditional", 0)
    total_count = support_count + reject_count + conditional_count

    return {
        "support_count": support_count,
        "reject_count": reject_count,
        "conditional_count": conditional_count,
        "total_count": total_count,
        "display": (
            f"Támogatja: {support_count} | "
            f"Elutasítja: {reject_count} | "
            f"Feltételes: {conditional_count}"
        ),
    }


def _build_consensus_payload(*, stance_counts: dict[str, int]) -> dict[str, Any]:
    support_count = stance_counts.get("support", 0)
    reject_count = stance_counts.get("reject", 0)

    direction: str | None = None
    count = 0

    if support_count >= CONSENSUS_THRESHOLD and support_count > reject_count:
        direction = "support"
        count = support_count
    elif reject_count >= CONSENSUS_THRESHOLD and reject_count > support_count:
        direction = "reject"
        count = reject_count

    if direction == "support":
        display = f"{count} persona támogatja"
    elif direction == "reject":
        display = f"{count} persona elutasítja"
    else:
        display = None

    return {
        "is_triggered": direction is not None,
        "direction": direction,
        "count": count if direction is not None else None,
        "threshold": CONSENSUS_THRESHOLD,
        "display": display,
    }


def _format_persona_count_label(*, completed: int, total: int) -> str:
    return f"{completed}/{total} persona"


def _format_persona_count_header_display(
    *, completed: int, total: int, final_status: str
) -> str:
    if final_status == "partial":
        return f"{completed}/{total} persona valaszolt"
    return _format_persona_count_label(completed=completed, total=total)


def _should_increment_monthly_cost(*, run_id: str) -> bool:
    try:
        existing_row = _load_run_row(run_id=run_id)
    except Exception as exc:
        # P11: DB unreachable — conservative default: skip increment to avoid double-counting
        with sentry_sdk.push_scope() as scope:
            scope.set_tag("run_id", run_id)
            scope.set_tag("error_code", "COST_GUARD_READ_FAILED")
            sentry_sdk.capture_exception(exc)
        return False
    if existing_row is None:
        return True
    status = existing_row.get("status")
    cost_value = existing_row.get("cost_usd")
    return not (status in FINAL_STATUSES and cost_value is not None)


def _load_run_row(*, run_id: str) -> dict[str, Any] | None:
    # P11: exceptions propagate to caller; caller decides the safe default
    supabase = get_supabase_client()
    result = (
        supabase.table("runs")
        .select("status,cost_usd")
        .eq("id", run_id)
        .limit(1)
        .execute()
    )
    rows = result.data or []
    if not rows:
        return None
    row = rows[0]
    return row if isinstance(row, dict) else None


def _normalize_cost(value: object) -> Decimal:
    try:
        normalized = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return Decimal("0")
    if not normalized.is_finite() or normalized < 0:  # P6: guard infinity
        return Decimal("0")
    return normalized


def _increment_monthly_cost(
    *, run_id: str, run_cost: Decimal, should_increment: bool
) -> None:
    if not should_increment:
        return

    month = datetime.now(UTC).strftime(
        "%Y-%m"
    )  # P7: UTC instead of date.today() local time
    try:
        supabase = get_supabase_client()
        existing = (
            supabase.table("cost_tracking")
            .select("total_usd")
            .eq("month", month)
            .limit(1)
            .execute()
            .data
            or []
        )
        existing_total = Decimal("0")
        if existing and isinstance(existing[0], dict):
            existing_total = _normalize_cost(existing[0].get("total_usd"))
        updated_total = existing_total + run_cost
        supabase.table(
            "cost_tracking"
        ).upsert(  # P2: upsert prevents duplicate-insert race
            {"month": month, "total_usd": str(updated_total)},
            on_conflict="month",
        ).execute()
    except Exception as exc:
        with sentry_sdk.push_scope() as scope:
            scope.set_tag("run_id", run_id)
            scope.set_tag("error_code", "COST_TRACKING_UPDATE_FAILED")
            scope.set_extra("month", month)
            scope.set_extra("run_cost", str(run_cost))
            sentry_sdk.capture_exception(exc)


def _dispatch_result_email(
    *, run_id: str, user_id: str, payload: dict[str, Any]
) -> None:
    recipient_email = _load_user_email(user_id=user_id)
    if recipient_email is None:
        with sentry_sdk.push_scope() as scope:
            scope.set_tag("run_id", run_id)
            scope.set_tag("error_code", "RESULT_EMAIL_RECIPIENT_NOT_FOUND")
            scope.set_extra("user_id", user_id)
            sentry_sdk.capture_message(
                f"Result email recipient not found for run_id={run_id}, user_id={user_id}",
                level="error",
            )
        return

    try:
        send_run_result_email(
            recipient_email=recipient_email,
            result_payload=payload,
            user_id=user_id,
        )
    except Exception as exc:
        failure_timestamp = datetime.now(UTC).isoformat()
        provider_error_code, provider_error_message = _extract_provider_error_metadata(
            exc
        )
        with sentry_sdk.push_scope() as scope:
            scope.set_tag("run_id", run_id)
            scope.set_tag("error_code", "RESULT_EMAIL_DISPATCH_FAILED")
            scope.set_extra("timestamp", failure_timestamp)
            scope.set_extra("status", payload.get("status"))
            scope.set_extra("persona_count", payload.get("persona_count_label"))
            scope.set_extra("provider_error_code", provider_error_code)
            scope.set_extra("provider_error_message", provider_error_message)
            sentry_sdk.capture_exception(exc)


def _extract_provider_error_metadata(exc: Exception) -> tuple[str | None, str]:
    provider_error_code = getattr(exc, "error_code", None) or getattr(exc, "code", None)
    if provider_error_code is None:
        status_code = getattr(exc, "status_code", None)
        if status_code is not None:
            provider_error_code = str(status_code)

    provider_error_message = str(exc) or exc.__class__.__name__
    return (
        str(provider_error_code) if provider_error_code is not None else None,
        provider_error_message,
    )


def _load_user_email(*, user_id: str) -> str | None:
    try:
        supabase = get_supabase_client()
        result = (
            supabase.table("users").select("email").eq("id", user_id).limit(1).execute()
        )
    except Exception:
        return None

    rows = result.data or []
    if not rows:
        return None

    email = rows[0].get("email") if isinstance(rows[0], dict) else None
    return email if isinstance(email, str) and email else None


def _update_run_row(*, run_id: str, payload: dict[str, Any]) -> None:
    try:
        supabase = get_supabase_client()
        supabase.table("runs").update(payload).eq("id", run_id).execute()
    except Exception as exc:
        with sentry_sdk.push_scope() as scope:
            scope.set_tag("run_id", run_id)
            scope.set_tag("error_code", "DB_UPDATE_FAILED")
            scope.set_extra("payload", payload)
            sentry_sdk.capture_exception(exc)


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
        sentry_sdk.capture_message(
            f"Persona threshold not met: {successful_count}/{required_count} personas succeeded "
            f"(run_id={run_id}, error_code={error_code})",
            level="error",
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
