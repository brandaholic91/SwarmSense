from __future__ import annotations

import asyncio
import logging
import time
from datetime import UTC, datetime
from typing import Any

from app import db
from app.models.persona import SynthesisResult
from app.services.llm_client import LLMClient, LLMProviderError, TokenUsage
from app.services.persona_engine import PersonaRunResult, execute_persona_engine
from app.services.synthesis_service import execute_synthesis

MIN_SUCCESSFUL_PERSONAS = 12
CONSENSUS_THRESHOLD = 15

logger = logging.getLogger("swarmsense.run")


async def process_run(
    *,
    run_id: str,
    topic: str,
    audience: str,
    llm_client: LLMClient | None = None,
) -> PersonaRunResult:
    started = time.monotonic()
    try:
        return await _process_run(
            run_id=run_id,
            topic=topic,
            audience=audience,
            llm_client=llm_client,
            started=started,
        )
    except Exception as exc:
        # bármilyen nem várt hiba: a futás ne maradjon running/composing állapotban
        # Naplóba csak a kivétel típusa (és a hibakód) kerül: az üzenet és a
        # lánc LLM-kimenetet, a szolgáltató nyers szövegét, témát tartalmazhat.
        logger.error("run %s failed unexpectedly: %s", run_id, _describe(exc))
        usage = exc.usage if isinstance(exc, LLMProviderError) else TokenUsage()
        try:
            db.update_run(
                run_id,
                status="failed",
                completed_at=datetime.now(UTC),
                input_tokens=usage.input_tokens,
                output_tokens=usage.output_tokens,
            )
        except Exception as update_exc:
            logger.error(
                "run %s could not be marked failed: %s", run_id, _describe(update_exc)
            )
        _log_summary(
            run_id=run_id, status="failed", started=started, usage=usage, dropped=None
        )
        raise


def _describe(exc: BaseException) -> str:
    """Naplózható leírás: kivételtípus, LLMProviderError esetén a hibakód is."""
    if isinstance(exc, LLMProviderError):
        return f"{type(exc).__name__} ({exc.error_code})"
    return type(exc).__name__


def _log_summary(
    *,
    run_id: str,
    status: str,
    started: float,
    usage: TokenUsage,
    dropped: int | None,
) -> None:
    logger.info(
        "run %s finished: status=%s elapsed=%.1fs input_tokens=%d "
        "output_tokens=%d dropped_personas=%s",
        run_id,
        status,
        time.monotonic() - started,
        usage.input_tokens,
        usage.output_tokens,
        "unknown" if dropped is None else dropped,
    )


async def _process_run(
    *,
    run_id: str,
    topic: str,
    audience: str,
    llm_client: LLMClient | None,
    started: float,
) -> PersonaRunResult:
    db.update_run(run_id, status="running", persona_count=0)

    def on_persona_completed(processed_count: int, total_personas: int) -> None:
        _ = total_personas
        try:
            db.update_run(run_id, status="running", persona_count=processed_count)
        except Exception as exc:
            # a haladásjelzés nem kritikus, a futás mehet tovább
            logger.error("run %s progress update failed: %s", run_id, _describe(exc))

    if llm_client is None:
        llm_client = LLMClient(session_id=f"swarmsense-{run_id}")

    result = await execute_persona_engine(
        topic=topic,
        audience=audience,
        llm_client=llm_client,
        on_persona_completed=on_persona_completed,
    )
    usage = TokenUsage(result.input_tokens, result.output_tokens)

    if result.successful_count < MIN_SUCCESSFUL_PERSONAS:
        _finish_run(
            run_id=run_id,
            status="failed",
            result=result,
            synthesis=None,
            usage=usage,
            started=started,
            persist_counts=False,
        )
        return result

    db.update_run(run_id, status="composing", persona_count=result.successful_count)

    synthesis: SynthesisResult | None = None
    try:
        synthesis, synthesis_usage = await execute_synthesis(
            personas=result.responses,
            topic=topic,
            audience=audience,
            llm_client=llm_client,
        )
        usage += synthesis_usage
    except Exception as exc:
        logger.error("run %s synthesis failed: %s", run_id, _describe(exc))
        if isinstance(exc, LLMProviderError):
            usage += exc.usage

    _finish_run(
        run_id=run_id,
        status=_resolve_final_status(result=result, synthesis=synthesis),
        result=result,
        synthesis=synthesis,
        usage=usage,
        started=started,
        persist_counts=True,
    )
    return result


def _finish_run(
    *,
    run_id: str,
    status: str,
    result: PersonaRunResult,
    synthesis: SynthesisResult | None,
    usage: TokenUsage,
    started: float,
    persist_counts: bool,
) -> None:
    fields: dict[str, Any] = {
        "status": status,
        "persona_count": result.successful_count,
        "completed_at": datetime.now(UTC),
        "input_tokens": usage.input_tokens,
        "output_tokens": usage.output_tokens,
    }
    if persist_counts:
        fields.update(
            support_count=sum(1 for r in result.responses if r.stance == "support"),
            reject_count=sum(1 for r in result.responses if r.stance == "reject"),
            conditional_count=sum(
                1 for r in result.responses if r.stance == "conditional"
            ),
        )
    if synthesis is not None:
        fields.update(
            synthesis_summary=synthesis.summary,
            synthesis_main_barriers=synthesis.main_barriers,
            synthesis_winning_conditions=synthesis.winning_conditions,
            synthesis_best_target_segment=synthesis.best_target_segment,
            synthesis_strategic_recommendation=synthesis.strategic_recommendation,
        )
    db.update_run(run_id, **fields)
    _log_summary(
        run_id=run_id,
        status=status,
        started=started,
        usage=usage,
        dropped=len(result.failures),
    )


def _resolve_final_status(
    *, result: PersonaRunResult, synthesis: SynthesisResult | None
) -> str:
    if result.successful_count < result.total_personas or synthesis is None:
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
    personas: list[dict[str, Any]] = result.handoff_payload

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
        "personas": personas,
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


def dispatch_run_processing(
    *,
    run_id: str,
    topic: str,
    audience: str,
    llm_client: LLMClient | None = None,
) -> None:
    # háttérfeladat: soha nem dobhat; a process_run már failed-re állította a futást
    try:
        asyncio.run(
            process_run(
                run_id=run_id,
                topic=topic,
                audience=audience,
                llm_client=llm_client,
            )
        )
    except Exception as exc:
        logger.error("run %s background task ended: %s", run_id, _describe(exc))
