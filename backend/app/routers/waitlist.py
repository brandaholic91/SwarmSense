from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.core.database import get_supabase_client
from app.core.errors import ErrorCode, error_response
from app.models.waitlist import WaitlistSignupRequest, WaitlistSignupResponse

router = APIRouter(prefix="/api/v1/waitlist", tags=["waitlist"])


def _is_unique_violation(exc: Exception) -> bool:
    code = getattr(exc, "code", None)
    if isinstance(code, str) and code == "23505":
        return True

    message = str(exc).lower()
    return "duplicate key" in message or "unique" in message


@router.post("", response_model=WaitlistSignupResponse)
async def join_waitlist(
    payload: WaitlistSignupRequest,
) -> WaitlistSignupResponse | JSONResponse:
    try:
        supabase = get_supabase_client()
        supabase.table("waitlist").insert({"email": payload.email}).execute()
        return WaitlistSignupResponse(status="joined")
    except Exception as exc:  # pragma: no cover - defensive server error fallback
        if _is_unique_violation(exc):
            return WaitlistSignupResponse(status="already_joined")
        return error_response(
            status_code=500,
            detail="Failed to join waitlist",
            code=ErrorCode.WAITLIST_SIGNUP_FAILED,
        )
