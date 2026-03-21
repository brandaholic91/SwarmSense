from __future__ import annotations

from typing import Literal

from pydantic import AwareDatetime, BaseModel, ConfigDict, field_validator


class RunSessionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    user_id: str
    topic: str
    audience: str
    role_answer: str
    use_case_answer: str

    @field_validator("user_id", mode="before")
    @classmethod
    def strip_id(cls, value: str) -> str:
        if isinstance(value, str):
            return value.strip()
        return value

    @field_validator("user_id")
    @classmethod
    def require_non_empty_id(cls, value: str) -> str:
        if not value:
            raise ValueError("Must not be empty")
        return value

    @field_validator("topic", "audience", "role_answer", "use_case_answer", mode="before")
    @classmethod
    def strip_text(cls, value: str) -> str:
        if isinstance(value, str):
            return value.strip()
        return value

    @field_validator("topic", "audience", "role_answer", "use_case_answer")
    @classmethod
    def require_non_empty_text(cls, value: str) -> str:
        if not value:
            raise ValueError("Must not be empty")
        return value


class RunSessionResponse(BaseModel):
    run_id: str
    status: Literal["queued", "running", "composing", "completed", "partial", "failed"]
    created_at: AwareDatetime
