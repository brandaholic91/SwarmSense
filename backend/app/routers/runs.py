from __future__ import annotations

import logging

from fastapi import APIRouter, BackgroundTasks, Header
from fastapi.responses import JSONResponse

from app import db
from app.core.errors import ErrorCode, error_response
from app.models.run import RunCreateRequest, RunCreateResponse, RunStatusResponse
from app.services import limits
from app.services.persona_engine import DEFAULT_PERSONA_COUNT
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


@router.get("/{run_id}/status", response_model=RunStatusResponse)
def get_run_status(run_id: str) -> RunStatusResponse | JSONResponse:
    run = db.get_run(run_id)
    if run is None:
        return error_response(
            status_code=404,
            detail="Run not found",
            code=ErrorCode.RUN_NOT_FOUND,
        )
    return RunStatusResponse(
        run_id=run["id"],
        status=run["status"],
        persona_count=max(run["persona_count"], 0),
        total_personas=DEFAULT_PERSONA_COUNT,
        updated_at=run["completed_at"] or run["created_at"],
    )
