from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/status", tags=["status"])


@router.get("")
def get_status() -> dict[str, str]:
    return {"status": "ok"}
