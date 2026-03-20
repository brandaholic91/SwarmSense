from __future__ import annotations

from typing import Literal
from uuid import UUID

from pydantic import AwareDatetime, BaseModel, ConfigDict, EmailStr, field_validator


class EmailCheckRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: EmailStr
    has_consent: bool
    consent_timestamp: AwareDatetime

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        if isinstance(value, str):
            return value.lower().strip()
        return value


class EmailCheckResponse(BaseModel):
    status: Literal["new", "returning"]
    redirect_to: str | None = None


class MagicLinkCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: EmailStr
    has_consent: bool
    consent_timestamp: AwareDatetime

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        if isinstance(value, str):
            return value.lower().strip()
        return value


class MagicLinkCreateResponse(BaseModel):
    status: Literal["sent"]


class VerifyTokenRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    token: UUID


class VerifyTokenResponse(BaseModel):
    user_id: str
