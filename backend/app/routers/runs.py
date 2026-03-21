from __future__ import annotations

from datetime import datetime
from typing import Any, Literal, cast

from fastapi import APIRouter, BackgroundTasks, HTTPException
from fastapi.responses import JSONResponse

from app.core.database import get_supabase_client
from app.core.errors import ErrorCode, error_response
from app.models.run import RunCreateRequest, RunCreateResponse, RunStatusResponse
from app.services.persona_engine import DEFAULT_PERSONA_COUNT
from app.services.run_processor import dispatch_run_processing

router = APIRouter(prefix="/api/v1/runs", tags=["runs"])
RunStatus = Literal["queued", "running", "composing", "completed", "partial", "failed"]
RUN_STATUSES: set[str] = {
    "queued",
    "running",
    "composing",
    "completed",
    "partial",
    "failed",
}


@router.post("", response_model=RunCreateResponse)
def create_run(
    payload: RunCreateRequest,
    background_tasks: BackgroundTasks,
) -> RunCreateResponse:
    try:
        supabase = get_supabase_client()
        result = (
            supabase.table("runs")
            .insert(
                {
                    "user_id": payload.user_id,
                    "topic": payload.topic,
                    "audience": payload.audience,
                    "status": "queued",
                }
            )
            .execute()
        )
    except Exception as exc:  # pragma: no cover - defensive server error fallback
        raise HTTPException(status_code=500, detail="Failed to create run") from exc

    rows = result.data or []
    if not rows:
        raise HTTPException(status_code=500, detail="Failed to create run")

    row = rows[0]
    if not isinstance(row, dict):
        raise HTTPException(status_code=500, detail="Failed to create run")

    row_data = cast(dict[str, Any], row)
    run_id = row_data.get("id")
    status = row_data.get("status")
    created_at = row_data.get("created_at")
    if (
        not isinstance(run_id, str)
        or not isinstance(status, str)
        or not isinstance(created_at, str)
    ):
        raise HTTPException(status_code=500, detail="Failed to create run")

    if status not in RUN_STATUSES:
        raise HTTPException(status_code=500, detail="Failed to create run")

    background_tasks.add_task(
        dispatch_run_processing,
        run_id=run_id,
        user_id=payload.user_id,
        topic=payload.topic,
        audience=payload.audience,
    )

    try:
        return RunCreateResponse(
            run_id=run_id,
            status=cast(RunStatus, status),
            created_at=datetime.fromisoformat(created_at.replace("Z", "+00:00")),
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Failed to create run") from exc


@router.get("/{run_id}/status", response_model=RunStatusResponse)
def get_run_status(run_id: str) -> RunStatusResponse | JSONResponse:
    supabase = get_supabase_client()
    try:
        result = (
            supabase.table("runs")
            .select("id,status,persona_count,completed_at,created_at")
            .eq("id", run_id)
            .limit(1)
            .execute()
        )
    except Exception as exc:  # pragma: no cover - defensive fallback
        raise HTTPException(
            status_code=500, detail="Failed to load run status"
        ) from exc

    rows = result.data or []
    if not rows:
        return error_response(
            status_code=404,
            detail="Run not found",
            code=ErrorCode.RUN_NOT_FOUND,
        )

    row = rows[0]
    if not isinstance(row, dict):
        raise HTTPException(status_code=500, detail="Failed to load run status")

    row_data = cast(dict[str, Any], row)
    status = row_data.get("status")
    if not isinstance(status, str) or status not in RUN_STATUSES:
        raise HTTPException(status_code=500, detail="Failed to load run status")

    persona_count_raw = row_data.get("persona_count")
    persona_count = int(persona_count_raw) if isinstance(persona_count_raw, int) else 0
    updated_at_raw = row_data.get("completed_at") or row_data.get("created_at")
    updated_at = (
        datetime.fromisoformat(updated_at_raw.replace("Z", "+00:00"))
        if isinstance(updated_at_raw, str)
        else None
    )

    try:
        return RunStatusResponse(
            run_id=run_id,
            status=cast(RunStatus, status),
            persona_count=max(persona_count, 0),
            total_personas=DEFAULT_PERSONA_COUNT,
            updated_at=updated_at,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail="Failed to load run status"
        ) from exc
