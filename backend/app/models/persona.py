from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict

PersonaStance = Literal["support", "reject", "conditional"]


class PersonaBlueprint(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    role: str
    risk_appetite: str
    decision_style: str
    organizational_role: str
    price_sensitivity: str
    technology_adoption_curve: str


class PersonaResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    role: str
    stance: PersonaStance
    primary_argument: str
    change_condition: str


class PersonaFailure(BaseModel):
    model_config = ConfigDict(extra="forbid")

    persona_name: str
    error_code: str
    error_message: str


class PersonaRunResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    total_personas: int
    successful_count: int
    responses: list[PersonaResponse]
    failures: list[PersonaFailure]
    handoff_payload: list[dict[str, Any]]
