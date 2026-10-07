from __future__ import annotations

import asyncio
import json
from typing import Any

import pytest

from app.models.persona import PersonaResponse
from app.services.llm_client import LLMClient
from app.services.synthesis_service import execute_synthesis

VALID_REPLY = {
    "summary": "Összefoglaló.",
    "main_barriers": ["Ár.", "Bizalom."],
    "winning_conditions": "Referenciák.",
    "best_target_segment": "Növekvő KKV-k.",
    "strategic_recommendation": "Pilot indítása.",
}

PERSONA = PersonaResponse(
    name="Persona 1",
    role="vezető",
    stance="support",
    primary_argument="Érv.",
    change_condition="Feltétel.",
    core_concern="Aggodalom.",
    buying_trigger="Trigger.",
)


def _synthesize(reply: dict[str, Any]):
    async def transport(
        url: str, headers: dict[str, str], payload: dict[str, Any]
    ) -> dict[str, Any]:
        return {
            "choices": [{"message": {"content": json.dumps(reply)}}],
            "usage": {"prompt_tokens": 10, "completion_tokens": 5},
        }

    client = LLMClient(session_id="test-session", transport=transport)
    return asyncio.run(
        execute_synthesis(
            personas=[PERSONA], topic="Árazás", audience="KKV vezetők", llm_client=client
        )
    )


def test_reply_echoing_the_response_format_is_accepted():
    # valódi futásban mért alak: a modell a kért öt kulcs elé visszaírja a kérés
    # `response_format` mezőjét ("type": "json_object")
    synthesis, usage = _synthesize({"type": "json_object", **VALID_REPLY})

    assert synthesis.model_dump() == VALID_REPLY
    assert (usage.input_tokens, usage.output_tokens) == (10, 5)


def test_reply_missing_a_required_key_is_rejected():
    reply = {k: v for k, v in VALID_REPLY.items() if k != "main_barriers"}
    with pytest.raises(ValueError):
        _synthesize({"type": "json_object", **reply})


def test_reply_with_wrong_type_is_rejected():
    with pytest.raises(ValueError):
        _synthesize({**VALID_REPLY, "main_barriers": "Ár."})
