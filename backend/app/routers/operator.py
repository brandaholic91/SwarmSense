from __future__ import annotations

from fastapi import APIRouter, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import get_settings
from app.models.operator import SendFollowupsResponse
from app.services.email_service import dispatch_followup_sequence

router = APIRouter(prefix="/api/v1/operator", tags=["operator"])

_bearer = HTTPBearer(auto_error=False)


@router.post("/send-followups", response_model=SendFollowupsResponse)
async def send_followups(
    credentials: HTTPAuthorizationCredentials | None = Security(_bearer),
) -> SendFollowupsResponse:
    settings = get_settings()
    if credentials is None or credentials.credentials != settings.operator_api_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden",
        )

    sent = dispatch_followup_sequence()
    return SendFollowupsResponse(sent=sent)
