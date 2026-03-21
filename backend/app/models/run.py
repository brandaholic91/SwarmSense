from __future__ import annotations

from typing import Literal

from pydantic import AwareDatetime, BaseModel, ConfigDict, field_validator


class RunCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    user_id: str
    topic: str
    audience: str

    @field_validator("topic", "audience", mode="before")
    @classmethod
    def strip_text(cls, value: str) -> str:
        if isinstance(value, str):
            return value.strip()
        return value

    @field_validator("topic", "audience")
    @classmethod
    def require_non_empty_text(cls, value: str) -> str:
        if not value:
            raise ValueError("Must not be empty")
        return value


class RunCreateResponse(BaseModel):
    run_id: str
    status: Literal["queued", "running", "composing", "completed", "partial", "failed"]
    created_at: AwareDatetime
