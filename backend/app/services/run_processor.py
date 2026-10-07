from __future__ import annotations

import asyncio
import logging
import time
from datetime import UTC, datetime
from typing import Any

from app import db
from app.models.persona import SynthesisResult
from app.services.blueprint_generator import BlueprintGenerationError
from app.services.events import EventSink, safe_emit
from app.services.llm_client import LLMClient, LLMProviderError, TokenUsage
from app.services import notifier, pdf_service
from app.services.persona_engine import PersonaRunResult, execute_persona_engine
from app.services.synthesis_service import execute_synthesis

MIN_SUCCESSFUL_PERSONAS = 12
CONSENSUS_THRESHOLD = 15

# a `run_failed` esemény hibakódjai
PERSONA_GENERATION_FAILED = "PERSONA_GENERATION_FAILED"
TOO_FEW_PERSONAS = "TOO_FEW_PERSONAS"
INTERNAL_ERROR = "INTERNAL_ERROR"

logger = logging.getLogger("swarmsense.run")


async def process_run(
    *,
    run_id: str,
    topic: str,
    audience: str,
    llm_client: LLMClient | None = None,
) -> PersonaRunResult | None:
    """Lefuttat egy futást. `None`, ha a persona-generálás elbukott (a futás
    ilyenkor `failed`, és nem dobunk); más váratlan hibánál a kivétel továbbmegy."""
    started = time.monotonic()

    def sink(type: str, **fields: Any) -> None:
        db.insert_event(run_id, type, **fields)

    try:
        return await _process_run(
            run_id=run_id,
            topic=topic,
            audience=audience,
            llm_client=llm_client,
            started=started,
            sink=sink,
        )
    except BlueprintGenerationError as exc:
        await _fail_run(
            run_id=run_id,
            error_code=PERSONA_GENERATION_FAILED,
            usage=exc.usage,
            started=started,
            dropped=None,
            sink=sink,
        )
        return None
    except Exception as exc:
        # bármilyen nem várt hiba: a futás ne maradjon running/composing állapotban
        # Naplóba csak a kivétel típusa (és a hibakód) kerül: az üzenet és a
        # lánc LLM-kimenetet, a szolgáltató nyers szövegét, témát tartalmazhat.
        logger.error("run %s failed unexpectedly: %s", run_id, _describe(exc))
        await _fail_run(
            run_id=run_id,
            error_code=INTERNAL_ERROR,
            usage=exc.usage if isinstance(exc, LLMProviderError) else TokenUsage(),
            started=started,
            dropped=None,
            sink=sink,
        )
        raise


async def _fail_run(
    *,
    run_id: str,
    error_code: str,
    usage: TokenUsage,
    started: float,
    dropped: int | None,
    sink: EventSink,
    persona_count: int | None = None,
) -> None:
    """A három bukási út közös lezárása: `failed` állapot, tokenek, esemény, napló."""
    fields: dict[str, Any] = {
        "status": "failed",
        "completed_at": datetime.now(UTC),
        "input_tokens": usage.input_tokens,
        "output_tokens": usage.output_tokens,
    }
    if persona_count is not None:
        fields["persona_count"] = persona_count
    wrote = True
    try:
        wrote = db.transition_run(
            run_id, from_statuses=("queued", "running", "composing"), **fields
        )
    except Exception as update_exc:
        logger.error(
            "run %s could not be marked failed: %s", run_id, _describe(update_exc)
        )
    # ha a takarító már lezárta a futást, ő írta az eseményt és küldte az értesítést
    if wrote:
        await safe_emit(sink, "run_failed", error_code=error_code)
        await asyncio.to_thread(notifier.notify_run_failed, run_id, error_code)
    _log_summary(
        run_id=run_id, status="failed", started=started, usage=usage, dropped=dropped
    )


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
    sink: EventSink,
) -> PersonaRunResult | None:
    if not db.transition_run(run_id, from_statuses=("queued",), status="running"):
        return _stop_closed(run_id)
    await safe_emit(sink, "run_started")

    if llm_client is None:
        llm_client = LLMClient(session_id=f"swarmsense-{run_id}")

    result = await execute_persona_engine(
        topic=topic,
        audience=audience,
        llm_client=llm_client,
        on_event=sink,
    )
    usage = TokenUsage(result.input_tokens, result.output_tokens)

    if result.successful_count < MIN_SUCCESSFUL_PERSONAS:
        await _fail_run(
            run_id=run_id,
            error_code=TOO_FEW_PERSONAS,
            usage=usage,
            started=started,
            dropped=len(result.failures),
            sink=sink,
            persona_count=result.successful_count,
        )
        return result

    if not db.transition_run(
        run_id,
        from_statuses=("running",),
        status="composing",
        persona_count=result.successful_count,
    ):
        return _stop_closed(run_id)

    synthesis: SynthesisResult | None = None
    synthesis_started = time.monotonic()
    await safe_emit(sink, "synthesis_started")
    try:
        synthesis, synthesis_usage = await execute_synthesis(
            personas=result.responses,
            topic=topic,
            audience=audience,
            llm_client=llm_client,
        )
        usage += synthesis_usage
        await safe_emit(
            sink,
            "synthesis_completed",
            duration_ms=_elapsed_ms(synthesis_started),
            input_tokens=synthesis_usage.input_tokens,
            output_tokens=synthesis_usage.output_tokens,
        )
    except Exception as exc:
        logger.error("run %s synthesis failed: %s", run_id, _describe(exc))
        failed_usage = TokenUsage()
        error_code = "MALFORMED_PROVIDER_OUTPUT"
        if isinstance(exc, LLMProviderError):
            failed_usage = exc.usage
            error_code = exc.error_code
        usage += failed_usage
        await safe_emit(
            sink,
            "synthesis_failed",
            error_code=error_code,
            duration_ms=_elapsed_ms(synthesis_started),
            input_tokens=failed_usage.input_tokens,
            output_tokens=failed_usage.output_tokens,
        )

    final_status = _resolve_final_status(result=result, synthesis=synthesis)
    stored = _store_result(
        run_id=run_id,
        final_status=final_status,
        result=result,
        synthesis=synthesis,
        usage=usage,
        topic=topic,
        audience=audience,
    )
    if not stored:
        return _stop_closed(run_id)
    # eredmény mentve → PDF → végső státusz → run_completed (a státusz addig `composing`)
    await _store_pdf(run_id)
    completed = _complete_run(
        run_id=run_id,
        status=final_status,
        result=result,
        usage=usage,
        started=started,
    )
    if completed:
        await safe_emit(sink, "run_completed")
    return result


def _elapsed_ms(started: float) -> int:
    return int((time.monotonic() - started) * 1000)


def _store_result(
    *,
    run_id: str,
    final_status: str,
    result: PersonaRunResult,
    synthesis: SynthesisResult | None,
    usage: TokenUsage,
    topic: str,
    audience: str,
) -> bool:
    """1. lépés: eredmény, számlálók, szintézis-oszlopok, tokenek; a státusz marad.
    Hamis, ha a futást közben lezárták (ilyenkor nem ír)."""
    fields: dict[str, Any] = {
        "persona_count": result.successful_count,
        "input_tokens": usage.input_tokens,
        "output_tokens": usage.output_tokens,
        "support_count": sum(1 for r in result.responses if r.stance == "support"),
        "reject_count": sum(1 for r in result.responses if r.stance == "reject"),
        "conditional_count": sum(
            1 for r in result.responses if r.stance == "conditional"
        ),
        "result": _build_result_payload(
            run_id=run_id,
            result=result,
            final_status=final_status,
            topic=topic,
            audience=audience,
            synthesis=synthesis,
        ),
    }
    if synthesis is not None:
        fields.update(
            synthesis_summary=synthesis.summary,
            synthesis_main_barriers=synthesis.main_barriers,
            synthesis_winning_conditions=synthesis.winning_conditions,
            synthesis_best_target_segment=synthesis.best_target_segment,
            synthesis_strategic_recommendation=synthesis.strategic_recommendation,
        )
    return db.transition_run(run_id, from_statuses=("composing",), **fields)


def _stop_closed(run_id: str) -> None:
    """A futást közben lezárták (pl. a takarító): nincs több írás, esemény, értesítés."""
    logger.warning("run %s was closed meanwhile, stopping", run_id)
    return None


async def _store_pdf(run_id: str) -> None:
    """PDF-készítés és mentés. A hibája nem buktatja a futást: a letöltő végpont
    első kérésre újrapróbálja. Naplóba csak a kivétel típusa kerül."""
    try:
        run = db.get_run(run_id)
        if run is None:
            return
        # a `completed_at` csak a PDF után kerül az adatbázisba; a futásidőt a
        # PDF-készítés kezdetéig számoljuk (a sablon nem olvas órát)
        run["completed_at"] = datetime.now(UTC)
        db.save_pdf(run_id, await pdf_service.generate_pdf(run))
    except Exception as exc:
        logger.error("run %s pdf failed: %s", run_id, _describe(exc))


def _complete_run(
    *,
    run_id: str,
    status: str,
    result: PersonaRunResult,
    usage: TokenUsage,
    started: float,
) -> bool:
    """2. lépés: végső státusz és `completed_at`, napló. Hamis, ha a futást közben
    lezárták (pl. a takarító): ilyenkor nem írunk és nincs `run_completed`."""
    if not db.finalize_run(run_id, status=status, completed_at=datetime.now(UTC)):
        logger.warning("run %s was closed meanwhile, not marked %s", run_id, status)
        return False
    _log_summary(
        run_id=run_id,
        status=status,
        started=started,
        usage=usage,
        dropped=len(result.failures),
    )
    return True


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
        "failed_personas": [
            {"name": failure.persona_name, "error_code": failure.error_code}
            for failure in result.failures
        ],
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
        return f"{completed}/{total} persona válaszolt"
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
