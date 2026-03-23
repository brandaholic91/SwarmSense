from __future__ import annotations

from typing import Literal

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field

# Error code constants for failed/partial runs (AC3 compliance)
DEFAULT_ERROR_CODE_FAILED = "RUN_FAILED"
DEFAULT_ERROR_CODE_PARTIAL = "RUN_PARTIAL"


class SendFollowupsResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    sent: int


class OperatorRunRow(BaseModel):
    model_config = ConfigDict(extra="forbid")

    run_id: str
    user_email: str
    topic: str = Field(..., max_length=500)
    audience: str = Field(..., max_length=500)
    status: Literal["queued", "running", "composing", "completed", "partial", "failed"]
    persona_count: int = Field(..., ge=0)
    cost_usd: float = Field(..., ge=0)
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


class OperatorQualifierResponseRow(BaseModel):
    model_config = ConfigDict(extra="forbid")

    user_email: str
    role_answer: str = Field(..., max_length=500)
    use_case_answer: str = Field(..., max_length=500)
    created_at: AwareDatetime


class OperatorQualifierResponsesResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    page: int
    page_size: int
    total: int
    items: list[OperatorQualifierResponseRow]


class OperatorCostResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    month: str
    total_usd: float = Field(..., ge=0)
    cap_usd: float = Field(..., ge=0)
    percentage: float = Field(..., ge=0)
    status: Literal["ok", "warning", "capped"]


class OperatorEmailStatsResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    window_days: int = Field(..., ge=1)
    result_emails_sent: int = Field(..., ge=0)
    result_delivery_rate: float = Field(..., ge=0, le=1)
    result_open_rate: float = Field(..., ge=0, le=1)
    magic_link_sent: int = Field(..., ge=0)
    magic_link_delivery_rate: float = Field(..., ge=0, le=1)
    followup_day1_sent: int = Field(..., ge=0)
    followup_day3_sent: int = Field(..., ge=0)
    followup_day7_sent: int = Field(..., ge=0)
    followup_delivery_rate: float = Field(..., ge=0, le=1)
    followup_open_rate: float = Field(..., ge=0, le=1)
    overall_delivery_rate: float = Field(..., ge=0, le=1)
