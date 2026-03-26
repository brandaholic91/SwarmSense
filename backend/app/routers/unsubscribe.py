from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import PlainTextResponse

from app.core.config import get_settings
from app.models.unsubscribe import UnsubscribeRequest, UnsubscribeResponse
from app.services.consent_service import mark_user_unsubscribed
from app.services.email_service import _verify_unsubscribe_token

router = APIRouter(prefix="/api/v1/unsubscribe", tags=["unsubscribe"])


@router.post("", response_model=UnsubscribeResponse)
async def unsubscribe(payload: UnsubscribeRequest) -> UnsubscribeResponse:
    settings = get_settings()
    if not _verify_unsubscribe_token(
        str(payload.user_id), payload.token, settings.internal_secret
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid unsubscribe token",
        )
    try:
        mark_user_unsubscribed(user_id=str(payload.user_id))
    except Exception as exc:  # pragma: no cover - defensive fallback
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process unsubscribe",
        ) from exc
    return UnsubscribeResponse(status="unsubscribed")


@router.get("", response_class=PlainTextResponse)
async def unsubscribe_via_link(
    user_id: UUID = Query(...),
    token: str = Query(...),
) -> PlainTextResponse:
    settings = get_settings()
    if not _verify_unsubscribe_token(str(user_id), token, settings.internal_secret):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid unsubscribe token",
        )
    try:
        mark_user_unsubscribed(user_id=str(user_id))
    except Exception as exc:  # pragma: no cover - defensive fallback
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process unsubscribe",
        ) from exc
    return PlainTextResponse(
        "Leiratkoztál a SwarmSense marketing e-mailekről."
    )
