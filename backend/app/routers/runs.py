from __future__ import annotations

import asyncio
import logging
from typing import Any

from fastapi import APIRouter, BackgroundTasks, Header, Query, Request, Response
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app import db
from app.core import pricing
from app.core.config import get_settings
from app.core.errors import ErrorCode, error_response
from app.models.run import (
    EmailRequest,
    EmailSentResponse,
    PriceInfo,
    RunCreateRequest,
    RunCreateResponse,
    RunDetailResponse,
    RunEvent,
    RunEventsResponse,
)
from app.services import email_service, limits, notifier, pdf_service
from app.services.run_processor import dispatch_run_processing

router = APIRouter(prefix="/api/v1/runs", tags=["runs"])
logger = logging.getLogger("swarmsense.run")


def _daily_limit_just_reached() -> bool:
    """Igaz, ha a most létrehozott futás töltötte be a napi keretet (így a
    betelés egyszer jelez). Az értesítés hibája nem akadályozhatja a futást."""
    try:
        return db.count_runs_since() == get_settings().runs_per_day
    except Exception as exc:
        logger.error("daily limit check failed: %s", type(exc).__name__)
        return False


@router.post("", response_model=RunCreateResponse)
def create_run(
    payload: RunCreateRequest,
    background_tasks: BackgroundTasks,
    x_client_ip: str | None = Header(default=None),
) -> RunCreateResponse | JSONResponse:
    try:
        ip_hash = limits.hash_ip(x_client_ip) if x_client_ip else None
        limit_code = limits.check_run_limits(ip_hash)
        if limit_code is None:
            row = db.create_run(
                topic=payload.topic, audience=payload.audience, ip_hash=ip_hash
            )
    except Exception as exc:
        # csak a kivétel típusa kerül a naplóba: a szöveg titkot (pl. DSN) hordozhat
        logger.error("run creation failed: %s", type(exc).__name__)
        return error_response(
            status_code=500,
            detail="Failed to create run",
            code=ErrorCode.RUN_START_FAILED,
        )
    if limit_code is not None:
        return error_response(
            status_code=429, detail="Run limit reached", code=limit_code
        )

    if _daily_limit_just_reached():
        background_tasks.add_task(notifier.notify_daily_limit_reached)
    background_tasks.add_task(
        dispatch_run_processing,
        run_id=row["id"],
        topic=payload.topic,
        audience=payload.audience,
    )
    return RunCreateResponse(
        run_id=row["id"], status=row["status"], created_at=row["created_at"]
    )


@router.get("/{run_id}", response_model=RunDetailResponse)
def get_run_detail(run_id: str) -> RunDetailResponse | JSONResponse:
    try:
        run = db.get_run(run_id)
        retry_count = (
            db.count_events(run_id, "persona_retry") if run is not None else 0
        )
        email_count = (
            db.count_email_requests(run_id=run_id) if run is not None else 0
        )
    except Exception as exc:
        # csak a kivétel típusa kerül a naplóba: a szöveg titkot (pl. DSN) hordozhat
        logger.error("run detail failed: %s", type(exc).__name__)
        return error_response(
            status_code=503,
            detail="Service unavailable",
            code=ErrorCode.SERVICE_UNAVAILABLE,
        )
    if run is None:
        return error_response(
            status_code=404, detail="Run not found", code=ErrorCode.RUN_NOT_FOUND
        )
    completed_at = run["completed_at"]
    duration_ms = (
        int((completed_at - run["created_at"]).total_seconds() * 1000)
        if completed_at is not None
        else None
    )
    has_result = run["status"] in ("completed", "partial")
    return RunDetailResponse(
        run_id=run["id"],
        status=run["status"],
        is_sample=run["is_sample"],
        topic=run["topic"],
        audience=run["audience"],
        created_at=run["created_at"],
        completed_at=completed_at,
        duration_ms=duration_ms,
        input_tokens=run["input_tokens"],
        output_tokens=run["output_tokens"],
        retry_count=retry_count,
        price=PriceInfo(**pricing.price_payload()),
        result=run["result"] if has_result else None,
        emails_remaining=max(0, get_settings().emails_per_run - email_count),
    )


async def _ensure_pdf(run: dict[str, Any], stored: bytes | None) -> bytes | None:
    """A tárolt PDF, vagy legenerálva és elmentve; None, ha nem sikerült."""
    if stored is not None:
        return stored
    # a futás közben nem sikerült PDF-et első kérésre újrapróbáljuk
    try:
        pdf = await pdf_service.generate_pdf(run)
        db.save_pdf(run["id"], pdf)
    except Exception as exc:
        logger.error("run %s pdf failed: %s", run["id"], type(exc).__name__)
        return None
    return pdf


@router.get("/{run_id}/pdf", response_model=None)
async def get_run_pdf(run_id: str) -> Response | JSONResponse:
    try:
        run = db.get_run(run_id)
        pdf = db.get_pdf(run_id) if run is not None else None
    except Exception as exc:
        # csak a kivétel típusa kerül a naplóba: a szöveg titkot (pl. DSN) hordozhat
        logger.error("run pdf lookup failed: %s", type(exc).__name__)
        return error_response(
            status_code=503,
            detail="Service unavailable",
            code=ErrorCode.SERVICE_UNAVAILABLE,
        )
    if run is None:
        return error_response(
            status_code=404, detail="Run not found", code=ErrorCode.RUN_NOT_FOUND
        )
    if run["status"] not in ("completed", "partial"):
        return error_response(
            status_code=409,
            detail="Run has no result",
            code=ErrorCode.RUN_NOT_FINISHED,
        )
    pdf = await _ensure_pdf(run, pdf)
    if pdf is None:
        return error_response(
            status_code=503,
            detail="PDF unavailable",
            code=ErrorCode.PDF_UNAVAILABLE,
        )
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="swarmsense-{run_id[:8]}.pdf"'
        },
    )


@router.get(
    "/{run_id}/events",
    response_model=RunEventsResponse,
    response_model_exclude_none=True,
)
def get_run_events(
    run_id: str, after: int = Query(default=0, ge=0)
) -> RunEventsResponse | JSONResponse:
    try:
        run = db.get_run(run_id)
        events = db.list_events(run_id, after=after) if run is not None else []
    except Exception as exc:
        # csak a kivétel típusa kerül a naplóba: a szöveg titkot (pl. DSN) hordozhat
        logger.error("run events failed: %s", type(exc).__name__)
        return error_response(
            status_code=503,
            detail="Service unavailable",
            code=ErrorCode.SERVICE_UNAVAILABLE,
        )
    if run is None:
        return error_response(
            status_code=404, detail="Run not found", code=ErrorCode.RUN_NOT_FOUND
        )
    return RunEventsResponse(
        status=run["status"],
        is_sample=run["is_sample"],
        topic=run["topic"],
        created_at=run["created_at"],
        price=PriceInfo(**pricing.price_payload()),
        events=[RunEvent(**event, at=event["created_at"]) for event in events],
    )


@router.post("/{run_id}/email", response_model=EmailSentResponse)
async def send_run_email(run_id: str, request: Request) -> EmailSentResponse | JSONResponse:
    # kézi validálás: a FastAPI alapértelmezett 422-es válasza visszaadná a beküldött címet
    try:
        payload = EmailRequest.model_validate(await request.json())
    except (ValidationError, ValueError):
        return error_response(
            status_code=422, detail="Invalid email", code=ErrorCode.INVALID_EMAIL
        )
    address = str(payload.email)
    settings = get_settings()

    try:
        run = db.get_run(run_id)
        if run is None:
            return error_response(
                status_code=404, detail="Run not found", code=ErrorCode.RUN_NOT_FOUND
            )
        if run["status"] not in ("completed", "partial"):
            return error_response(
                status_code=409,
                detail="Run has no result",
                code=ErrorCode.RUN_NOT_FINISHED,
            )
        if not settings.resend_api_key or not settings.email_from:
            return error_response(
                status_code=503,
                detail="Email is not configured",
                code=ErrorCode.EMAIL_NOT_CONFIGURED,
            )
        run_count = db.count_email_requests(run_id=run_id)
        if run_count >= settings.emails_per_run:
            return error_response(
                status_code=429,
                detail="Email limit for this run reached",
                code=ErrorCode.EMAIL_RUN_LIMIT_REACHED,
            )
        if db.count_email_requests(hours=24) >= settings.emails_per_day:
            return error_response(
                status_code=429,
                detail="Daily email limit reached",
                code=ErrorCode.EMAIL_DAILY_LIMIT_REACHED,
            )
        stored = db.get_pdf(run_id)
    except Exception as exc:
        logger.error("run email lookup failed: %s", type(exc).__name__)
        return error_response(
            status_code=503,
            detail="Service unavailable",
            code=ErrorCode.SERVICE_UNAVAILABLE,
        )

    pdf = await _ensure_pdf(run, stored)
    if pdf is None:
        return error_response(
            status_code=503, detail="PDF unavailable", code=ErrorCode.PDF_UNAVAILABLE
        )

    try:
        request_id = db.create_email_request(run_id, address)
    except Exception as exc:
        logger.error("run email request failed: %s", type(exc).__name__)
        return error_response(
            status_code=503,
            detail="Service unavailable",
            code=ErrorCode.SERVICE_UNAVAILABLE,
        )
    try:
        await asyncio.to_thread(
            email_service.send_report_email,
            to=address,
            topic=run["topic"],
            run_id=run_id,
            pdf=pdf,
        )
        db.mark_email_sent(request_id)
    except Exception as exc:
        # a cím és a szolgáltató üzenete nem kerül a naplóba: csak a típus és a kód
        logger.error(
            "run %s email failed: %s (%s)",
            run_id,
            type(exc).__name__,
            ErrorCode.EMAIL_SEND_FAILED.value,
        )
        return error_response(
            status_code=502,
            detail="Email send failed",
            code=ErrorCode.EMAIL_SEND_FAILED,
        )
    return EmailSentResponse(
        status="sent", emails_remaining=max(0, settings.emails_per_run - run_count - 1)
    )
