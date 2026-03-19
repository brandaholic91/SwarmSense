from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/runs", tags=["runs"])


@router.post("")
def create_run() -> dict[str, str]:
    return {"status": "queued"}
