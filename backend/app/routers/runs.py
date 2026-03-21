from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, HTTPException

from app.core.database import get_supabase_client
from app.models.run import RunCreateRequest, RunCreateResponse
from app.services.run_processor import dispatch_run_processing

router = APIRouter(prefix="/api/v1/runs", tags=["runs"])


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
    run_id = row.get("id")
    status = row.get("status")
    created_at = row.get("created_at")
    if (
        not isinstance(run_id, str)
        or not isinstance(status, str)
        or not isinstance(created_at, str)
    ):
        raise HTTPException(status_code=500, detail="Failed to create run")

    background_tasks.add_task(
        dispatch_run_processing,
        run_id=run_id,
        user_id=payload.user_id,
        topic=payload.topic,
        audience=payload.audience,
    )

    return RunCreateResponse(run_id=run_id, status=status, created_at=created_at)
