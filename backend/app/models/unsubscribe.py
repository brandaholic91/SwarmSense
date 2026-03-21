from __future__ import annotations

from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class UnsubscribeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    user_id: UUID


class UnsubscribeResponse(BaseModel):
    status: Literal["unsubscribed"]
