from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.core.database import get_supabase_client
from app.models.auth import EmailCheckRequest, EmailCheckResponse

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post(
    "/check-email", response_model=EmailCheckResponse, response_model_exclude_none=True
)
async def check_email(payload: EmailCheckRequest) -> EmailCheckResponse:
    try:
        supabase = get_supabase_client()
        user_result = (
            supabase.table("users")
            .select("id")
            .eq("email", payload.email)
            .limit(1)
            .execute()
        )
    except Exception as exc:  # pragma: no cover - defensive server error fallback
        raise HTTPException(status_code=500, detail="Failed to check email") from exc

    users = user_result.data or []
    if not users:
        return EmailCheckResponse(status="new")

    user_id = users[0]["id"]

    try:
        completed_run_result = (
            supabase.table("runs")
            .select("id")
            .eq("user_id", user_id)
            .in_("status", ["completed", "partial"])
            .limit(1)
            .execute()
        )
    except Exception as exc:  # pragma: no cover - defensive server error fallback
        raise HTTPException(status_code=500, detail="Failed to check email") from exc

    completed_runs = completed_run_result.data or []
    if completed_runs:
        return EmailCheckResponse(status="returning", redirect_to="/blocked")

    return EmailCheckResponse(status="new")
