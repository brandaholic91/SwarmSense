from __future__ import annotations

import logging

from fastapi import APIRouter, BackgroundTasks, Header, Query
from fastapi.responses import JSONResponse

from app import db
from app.core import pricing
from app.core.errors import ErrorCode, error_response
from app.models.run import (
    PriceInfo,
    RunCreateRequest,
    RunCreateResponse,
    RunDetailResponse,
    RunEvent,
    RunEventsResponse,
)
from app.services import limits
from app.services.run_processor import dispatch_run_processing

router = APIRouter(prefix="/api/v1/runs", tags=["runs"])
logger = logging.getLogger("swarmsense.run")


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
