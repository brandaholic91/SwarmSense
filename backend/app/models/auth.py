from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator


class EmailCheckRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: EmailStr
    has_consent: bool
    consent_timestamp: datetime

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        if isinstance(value, str):
            return value.lower().strip()
        return value


class EmailCheckResponse(BaseModel):
    status: Literal["new", "returning"]
    redirect_to: str | None = None
