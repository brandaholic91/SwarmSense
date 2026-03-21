from __future__ import annotations

from typing import Literal

from pydantic import AwareDatetime, BaseModel, ConfigDict, field_validator


class QualifierCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    run_id: str
    user_id: str
    role_answer: str
    use_case_answer: str

    @field_validator("role_answer", "use_case_answer", mode="before")
    @classmethod
    def strip_text(cls, value: str) -> str:
        if isinstance(value, str):
            return value.strip()
        return value

    @field_validator("role_answer", "use_case_answer")
    @classmethod
    def require_non_empty_text(cls, value: str) -> str:
        if not value:
            raise ValueError("Must not be empty")
        return value


class QualifierCreateResponse(BaseModel):
    status: Literal["recorded"]
    qualifier_id: str
    created_at: AwareDatetime
