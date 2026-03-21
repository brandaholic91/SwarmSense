from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import PlainTextResponse

from app.core.database import get_supabase_client
from app.models.unsubscribe import UnsubscribeRequest, UnsubscribeResponse

router = APIRouter(prefix="/api/v1/unsubscribe", tags=["unsubscribe"])


def _mark_user_unsubscribed(*, user_id: UUID) -> None:
    now = datetime.now(UTC).isoformat()
    supabase = get_supabase_client()
    (
        supabase.table("users")
        .update({"unsubscribed_at": now})
        .eq("id", str(user_id))
        .is_("unsubscribed_at", "null")
        .execute()
    )


@router.post("", response_model=UnsubscribeResponse)
async def unsubscribe(payload: UnsubscribeRequest) -> UnsubscribeResponse:
    try:
        _mark_user_unsubscribed(user_id=payload.user_id)
    except Exception as exc:  # pragma: no cover - defensive fallback
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process unsubscribe",
        ) from exc
    return UnsubscribeResponse(status="unsubscribed")


@router.get("", response_class=PlainTextResponse)
async def unsubscribe_via_link(user_id: UUID = Query(...)) -> PlainTextResponse:
    try:
        _mark_user_unsubscribed(user_id=user_id)
    except Exception as exc:  # pragma: no cover - defensive fallback
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process unsubscribe",
        ) from exc
    return PlainTextResponse(
        "You are now unsubscribed from SwarmSense follow-up emails."
    )
