from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.core.database import get_supabase_client
from app.models.qualifier import QualifierCreateRequest, QualifierCreateResponse

router = APIRouter(prefix="/api/v1/qualifier-responses", tags=["qualifier"])


@router.post("", response_model=QualifierCreateResponse)
def create_qualifier_response(
    payload: QualifierCreateRequest,
) -> QualifierCreateResponse:
    try:
        supabase = get_supabase_client()
        result = (
            supabase.table("qualifier_responses")
            .insert(
                {
                    "run_id": payload.run_id,
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

    rows = result.data or []
    if not rows:
        raise HTTPException(status_code=500, detail="Failed to save qualifier response")

    row = rows[0]
    qualifier_id = row.get("id")
    created_at = row.get("created_at")
    if not isinstance(qualifier_id, str) or not isinstance(created_at, str):
        raise HTTPException(status_code=500, detail="Failed to save qualifier response")

    return QualifierCreateResponse(
        status="recorded",
        qualifier_id=qualifier_id,
        created_at=created_at,
    )
