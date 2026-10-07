from __future__ import annotations

from typing import Annotated, Any, Literal

from pydantic import AwareDatetime, BaseModel, ConfigDict, StringConstraints

MAX_FIELD_LENGTH = 500

# szóközvágás után 1-500 karakter
RunText = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=MAX_FIELD_LENGTH),
]


class RunCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    topic: RunText
    audience: RunText


class RunCreateResponse(BaseModel):
    run_id: str
    status: Literal["queued", "running", "composing", "completed", "partial", "failed"]
    created_at: AwareDatetime


RunStatus = Literal["queued", "running", "composing", "completed", "partial", "failed"]


class PriceInfo(BaseModel):
    input_per_million_usd: float
    output_per_million_usd: float


class RunEvent(BaseModel):
    id: int
    type: str
    persona_index: int | None = None
    persona_name: str | None = None
    attempt: int | None = None
    error_code: str | None = None
    duration_ms: int | None = None
    input_tokens: int | None = None
    output_tokens: int | None = None
    at: AwareDatetime


class RunEventsResponse(BaseModel):
    status: RunStatus
    is_sample: bool
    topic: str
    created_at: AwareDatetime
    price: PriceInfo
    events: list[RunEvent]


class RunDetailResponse(BaseModel):
    run_id: str
    status: RunStatus
    is_sample: bool
    topic: str
    audience: str
    created_at: AwareDatetime
    completed_at: AwareDatetime | None
    duration_ms: int | None
    input_tokens: int
    output_tokens: int
    retry_count: int
    price: PriceInfo
    result: dict[str, Any] | None
