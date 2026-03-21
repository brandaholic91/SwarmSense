from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import uuid4

from fastapi import APIRouter, HTTPException, status

from app.core.database import get_supabase_client
from app.core.errors import ErrorCode, error_response
from app.models.auth import (
    EmailCheckRequest,
    EmailCheckResponse,
    MagicLinkCreateRequest,
    MagicLinkCreateResponse,
    VerifyTokenRequest,
    VerifyTokenResponse,
)
from app.services.email_service import send_magic_link_email
from app.core.config import get_settings

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post(
    "/check-email", response_model=EmailCheckResponse, response_model_exclude_none=True
)
async def check_email(payload: EmailCheckRequest) -> EmailCheckResponse:
    if not payload.has_consent:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Consent is required",
        )

    settings = get_settings()

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

    if settings.disable_single_run_limit:
        return EmailCheckResponse(status="new")

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


@router.post("/magic-link", response_model=MagicLinkCreateResponse)
async def create_magic_link(payload: MagicLinkCreateRequest) -> MagicLinkCreateResponse:
    if not payload.has_consent:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Consent is required",
        )

    now = datetime.now(UTC)
    try:
        supabase = get_supabase_client()
        existing_user = (
            supabase.table("users")
            .select("id")
            .eq("email", payload.email)
            .limit(1)
            .execute()
        )
    except Exception as exc:  # pragma: no cover - defensive server error fallback
        raise HTTPException(
            status_code=500, detail="Failed to generate magic link"
        ) from exc

    users = existing_user.data or []
    if users:
        user_id = users[0]["id"]
        try:
            # P-11: Update consent for returning user with server-side timestamp
            supabase.table("users").update(
                {"has_consent": True, "consent_timestamp": now.isoformat()}
            ).eq("id", user_id).execute()
        except Exception as exc:  # pragma: no cover - defensive server error fallback
            raise HTTPException(
                status_code=500, detail="Failed to generate magic link"
            ) from exc
    else:
        try:
            created_user = (
                supabase.table("users")
                .insert(
                    {
                        "email": payload.email,
                        "has_consent": True,
                        "consent_timestamp": now.isoformat(),  # P-6: server-side now()
                    }
                )
                .execute()
            )
        except Exception as exc:  # pragma: no cover - defensive server error fallback
            raise HTTPException(
                status_code=500, detail="Failed to generate magic link"
            ) from exc

        created_users = created_user.data or []
        if not created_users:
            raise HTTPException(status_code=500, detail="Failed to generate magic link")
        user_id = created_users[0]["id"]

    token = str(uuid4())
    expires_at = now + timedelta(hours=24)

    try:
        # P-3: Invalidate existing unused tokens for this user before issuing a new one
        supabase.table("magic_link_tokens").update({"used_at": now.isoformat()}).eq(
            "user_id", user_id
        ).is_("used_at", "null").execute()

        supabase.table("magic_link_tokens").insert(
            {
                "token": token,
                "user_id": user_id,
                "expires_at": expires_at.isoformat(),
                "used_at": None,
            }
        ).execute()

        settings = get_settings()
        verify_url = f"{str(settings.frontend_origin).rstrip('/')}/verify?token={token}"
        send_magic_link_email(payload.email, verify_url)
    except Exception as exc:  # pragma: no cover - defensive server error fallback
        raise HTTPException(
            status_code=500, detail="Failed to generate magic link"
        ) from exc

    return MagicLinkCreateResponse(status="sent")


@router.post(
    "/verify", response_model=VerifyTokenResponse, response_model_exclude_none=True
)
async def verify_magic_link(payload: VerifyTokenRequest):
    token = str(payload.token)
    now = datetime.now(UTC)

    try:
        supabase = get_supabase_client()
        token_result = (
            supabase.table("magic_link_tokens")
            .select("token,user_id,expires_at,used_at")
            .eq("token", token)
            .limit(1)
            .execute()
        )
    except Exception as exc:  # pragma: no cover - defensive server error fallback
        raise HTTPException(status_code=500, detail="Failed to verify token") from exc

    rows = token_result.data or []
    if not rows:
        return error_response(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Magic link token invalid",
            code=ErrorCode.TOKEN_INVALID,
        )

    row = rows[0]
    if row.get("used_at") is not None:
        return error_response(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Magic link token invalid",
            code=ErrorCode.TOKEN_INVALID,
        )

    expires_at_raw = row.get("expires_at")
    if not isinstance(expires_at_raw, str):
        raise HTTPException(status_code=500, detail="Failed to verify token")

    # P-14: Handle all Postgres timestamptz formats (space separator, Z suffix, offset)
    expires_at = datetime.fromisoformat(
        expires_at_raw.replace(" ", "T").replace("Z", "+00:00")
    )
    if expires_at <= now:
        # P-10: Mark expired token as used to prevent indefinite replay probing
        try:
            supabase.table("magic_link_tokens").update({"used_at": now.isoformat()}).eq(
                "token", token
            ).is_("used_at", "null").execute()
        except Exception:  # pragma: no cover
            pass  # best-effort; don't block the error response
        return error_response(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Magic link token expired",
            code=ErrorCode.TOKEN_EXPIRED,
        )

    try:
        updated = (
            supabase.table("magic_link_tokens")
            .update({"used_at": now.isoformat()})
            .eq("token", token)
            .is_("used_at", "null")
            .execute()
        )
    except Exception as exc:  # pragma: no cover - defensive server error fallback
        raise HTTPException(status_code=500, detail="Failed to verify token") from exc

    updated_rows = updated.data or []
    if not updated_rows:
        return error_response(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Magic link token invalid",
            code=ErrorCode.TOKEN_INVALID,
        )

    return VerifyTokenResponse(user_id=row["user_id"])
