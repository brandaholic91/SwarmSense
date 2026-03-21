from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class SendFollowupsResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    sent: int
