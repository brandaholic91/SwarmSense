from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, HTTPException

from app.core.database import get_supabase_client
from app.models.run_session import RunSessionRequest, RunSessionResponse
from app.services.run_processor import dispatch_run_processing

router = APIRouter(prefix="/api/v1/run-sessions", tags=["run-sessions"])


@router.post("", response_model=RunSessionResponse)
def create_run_session(
    payload: RunSessionRequest,
    background_tasks: BackgroundTasks,
) -> RunSessionResponse:
    supabase = get_supabase_client()

    # Step 1: insert run (qualifier_responses.run_id is NOT NULL FK)
    try:
        run_result = (
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

    run_rows = run_result.data or []
    if not run_rows:
        raise HTTPException(status_code=500, detail="Failed to create run")

    run_row = run_rows[0]
    run_id = run_row.get("id")
    status = run_row.get("status")
    created_at = run_row.get("created_at")
    if (
        not isinstance(run_id, str)
        or not isinstance(status, str)
        or not isinstance(created_at, str)
    ):
        raise HTTPException(status_code=500, detail="Failed to create run")

    # Step 2: insert qualifier response
    try:
        (
            supabase.table("qualifier_responses")
            .insert(
                {
                    "run_id": run_id,
                    "user_id": payload.user_id,
                    "role_answer": payload.role_answer,
                    "use_case_answer": payload.use_case_answer,
                }
            )
            .execute()
        )
    except Exception as exc:  # pragma: no cover - defensive server error fallback
        raise HTTPException(
            status_code=500, detail="Failed to save qualifier response"
        ) from exc

    background_tasks.add_task(
        dispatch_run_processing,
        run_id=run_id,
        user_id=payload.user_id,
        topic=payload.topic,
        audience=payload.audience,
    )

    try:
        return RunSessionResponse(run_id=run_id, status=status, created_at=created_at)
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Failed to create run") from exc
