from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator


class WaitlistSignupRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: EmailStr

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        if isinstance(value, str):
            return value.lower().strip()
        return value


class WaitlistSignupResponse(BaseModel):
    status: Literal["joined", "already_joined"]
