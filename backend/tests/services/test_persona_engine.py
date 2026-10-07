from __future__ import annotations

import asyncio

import pytest

from app.services.llm_client import LLMProviderError, TokenUsage
from app.services.persona_engine import (
    HUNGARIAN_MARKET_CONTEXT,
    HUNGARIAN_SYSTEM_PROMPT,
    build_persona_blueprints,
    build_persona_user_prompt,
    execute_persona_engine,
    normalize_persona_response,
)


def test_build_persona_blueprints_returns_unique_profiles() -> None:
    blueprints = build_persona_blueprints()

    assert 15 <= len(blueprints) <= 20
    assert len({item.name for item in blueprints}) == len(blueprints)
    assert all(item.risk_appetite for item in blueprints)
    assert all(item.decision_style for item in blueprints)
    assert all(item.organizational_role for item in blueprints)
    assert all(item.price_sensitivity for item in blueprints)
    assert all(item.technology_adoption_curve for item in blueprints)


def test_prompt_is_hungarian_and_market_contextual() -> None:
    persona = build_persona_blueprints(total_personas=15)[0]

    prompt = build_persona_user_prompt(
        persona=persona,
        topic="Árazási stratégia",
        audience="Magyar KKV pénzügyi vezetők",
    )

    assert "Kutatási téma" in prompt
    assert "Magyar" in prompt or "magyar" in prompt
    assert "JSON objektummal" in prompt
    assert HUNGARIAN_MARKET_CONTEXT in HUNGARIAN_SYSTEM_PROMPT
    assert "kizárólag" in HUNGARIAN_SYSTEM_PROMPT.lower()
    assert "markdown" in HUNGARIAN_SYSTEM_PROMPT.lower()


def test_normalize_persona_response_enforces_schema() -> None:
    normalized = normalize_persona_response(
        {
            "name": "Teszt Persona",
            "role": "Founder",
            "stance": "support",
            "primary_argument": "A modell jol illeszkedik a magyar piachoz.",
            "change_condition": "Akkor valtoztatnek, ha a CAC tartosan no.",
            "core_concern": "Fel a vendor lock-intol.",
            "buying_trigger": "Pozitiv referenciak esetén azonnal dontene.",
        }
    )

    assert normalized.stance == "support"

    with pytest.raises(ValueError):
        normalize_persona_response(
            {
                "name": "Teszt Persona",
                "role": "Founder",
                "stance": "unknown",
                "primary_argument": "invalid",
                "change_condition": "invalid",
                "core_concern": "invalid",
                "buying_trigger": "invalid",
            }
        )


def test_execute_persona_engine_uses_parallel_dispatch_and_semaphore() -> None:
    max_inflight = 0
    current_inflight = 0

    class FakeClient:
        async def generate_json(
            self, *, system_prompt: str, user_prompt: str, temperature: float = 0.3
        ):
            nonlocal max_inflight
            nonlocal current_inflight

            assert system_prompt
            assert user_prompt

            current_inflight += 1
            max_inflight = max(max_inflight, current_inflight)
            await asyncio.sleep(0.01)
            current_inflight -= 1
            return (
                {
                    "name": "Persona",
                    "role": "Role",
                    "stance": "conditional",
                    "primary_argument": "Erv",
                    "change_condition": "Feltetel",
                    "core_concern": "Aggodalom",
                    "buying_trigger": "Trigger",
                },
                TokenUsage(10, 5),
            )

    result = asyncio.run(
        execute_persona_engine(
            topic="Tema",
            audience="Kozonseg",
            llm_client=FakeClient(),
            concurrency_limit=3,
            blueprints=build_persona_blueprints(total_personas=18),
        )
    )

    assert result.successful_count == 18
    assert len(result.failures) == 0
    assert max_inflight <= 3
    assert result.input_tokens == 180
    assert result.output_tokens == 90


def test_execute_persona_engine_collects_provider_failures() -> None:
    class FailingClient:
        async def generate_json(
            self, *, system_prompt: str, user_prompt: str, temperature: float = 0.3
        ):
            raise LLMProviderError(
                error_code="RATE_LIMITED",
                message="rate limited",
            )

    result = asyncio.run(
        execute_persona_engine(
            topic="Tema",
            audience="Kozonseg",
            llm_client=FailingClient(),
            blueprints=build_persona_blueprints(total_personas=15),
        )
    )

    assert result.successful_count == 0
    assert len(result.failures) == 15
    assert all(item.error_code == "RATE_LIMITED" for item in result.failures)
