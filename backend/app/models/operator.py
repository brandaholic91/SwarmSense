from __future__ import annotations

from typing import Literal

from pydantic import AwareDatetime, BaseModel, ConfigDict


class SendFollowupsResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    sent: int


class OperatorRunRow(BaseModel):
    model_config = ConfigDict(extra="forbid")

    run_id: str
    user_email: str
    topic: str
    audience: str
    status: Literal["queued", "running", "composing", "completed", "partial", "failed"]
    persona_count: int
    cost_usd: float
    created_at: AwareDatetime
    completed_at: AwareDatetime | None = None
    error_code: str | None = None
    error_at: AwareDatetime | None = None


class OperatorRunsResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    page: int
    page_size: int
    total: int
    items: list[OperatorRunRow]
