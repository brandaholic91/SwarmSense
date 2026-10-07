from __future__ import annotations

from typing import Annotated, Literal

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


class RunStatusResponse(BaseModel):
    run_id: str
    status: Literal["queued", "running", "composing", "completed", "partial", "failed"]
    persona_count: int
    total_personas: int
    updated_at: AwareDatetime | None = None
