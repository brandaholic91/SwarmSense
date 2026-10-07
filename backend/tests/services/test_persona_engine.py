from __future__ import annotations

import asyncio

import pytest

from app.services.blueprint_generator import (
    BlueprintGenerationError,
    generate_persona_blueprints,
)
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
            self,
            *,
            system_prompt: str,
            user_prompt: str,
            temperature: float = 0.3,
            on_retry=None,
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
            self,
            *,
            system_prompt: str,
            user_prompt: str,
            temperature: float = 0.3,
            on_retry=None,
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


def test_failed_persona_tokens_are_still_counted() -> None:
    valid = {
        "name": "Persona",
        "role": "Role",
        "stance": "conditional",
        "primary_argument": "Erv",
        "change_condition": "Feltetel",
        "core_concern": "Aggodalom",
        "buying_trigger": "Trigger",
    }
    calls = 0

    class MixedClient:
        async def generate_json(
            self,
            *,
            system_prompt: str,
            user_prompt: str,
            temperature: float = 0.3,
            on_retry=None,
        ):
            nonlocal calls
            calls += 1
            body = {"name": "csak ennyi"} if calls == 1 else valid
            return body, TokenUsage(10, 5)

    result = asyncio.run(
        execute_persona_engine(
            topic="Tema",
            audience="Kozonseg",
            llm_client=MixedClient(),
            blueprints=build_persona_blueprints(total_personas=18),
        )
    )

    assert result.successful_count == 17
    assert len(result.failures) == 1
    assert result.failures[0].error_code == "MALFORMED_PROVIDER_OUTPUT"
    assert result.input_tokens == 180
    assert result.output_tokens == 90


def test_provider_error_usage_is_counted_for_failed_persona() -> None:
    class InvalidJsonClient:
        async def generate_json(
            self,
            *,
            system_prompt: str,
            user_prompt: str,
            temperature: float = 0.3,
            on_retry=None,
        ):
            raise LLMProviderError(
                error_code="INVALID_JSON",
                message="nem json",
                usage=TokenUsage(10, 5),
            )

    result = asyncio.run(
        execute_persona_engine(
            topic="Tema",
            audience="Kozonseg",
            llm_client=InvalidJsonClient(),
            blueprints=build_persona_blueprints(total_personas=15),
        )
    )

    assert len(result.failures) == 15
    assert result.input_tokens == 150
    assert result.output_tokens == 75


# --- események ---------------------------------------------------------------

VALID_RESPONSE = {
    "name": "Persona",
    "role": "Role",
    "stance": "conditional",
    "primary_argument": "Erv",
    "change_condition": "Feltetel",
    "core_concern": "Aggodalom",
    "buying_trigger": "Trigger",
}


def _collecting_sink() -> tuple[list[tuple[str, dict]], object]:
    events: list[tuple[str, dict]] = []

    def sink(type_: str, **fields) -> None:
        events.append((type_, fields))

    return events, sink


def _name_in(user_prompt: str) -> str:
    return user_prompt.split("- Név: ", 1)[1].split("\n", 1)[0]


def _run_engine(client, sink, **kwargs):
    return asyncio.run(
        execute_persona_engine(
            topic="Tema",
            audience="Kozonseg",
            llm_client=client,
            on_event=sink,
            **kwargs,
        )
    )


def test_events_respect_concurrency_limit() -> None:
    class SlowClient:
        async def generate_json(
            self, *, system_prompt, user_prompt, temperature=0.3, on_retry=None
        ):
            await asyncio.sleep(0.01)
            return VALID_RESPONSE, TokenUsage(10, 5)

    events, sink = _collecting_sink()
    _run_engine(
        SlowClient(), sink, blueprints=build_persona_blueprints(total_personas=18)
    )

    in_flight = 0
    peak = 0
    for type_, _ in events:
        if type_ == "persona_started":
            in_flight += 1
        elif type_ in ("persona_completed", "persona_failed"):
            in_flight -= 1
        peak = max(peak, in_flight)
        assert in_flight <= 5
    assert peak == 5


def test_persona_events_carry_index_name_attempt_tokens() -> None:
    blueprints = build_persona_blueprints(total_personas=18)
    target = blueprints[2]

    class RetryingClient:
        async def generate_json(
            self, *, system_prompt, user_prompt, temperature=0.3, on_retry=None
        ):
            if _name_in(user_prompt) == target.name:
                await on_retry(2, "RATE_LIMITED")
            return VALID_RESPONSE, TokenUsage(10, 5)

    events, sink = _collecting_sink()
    _run_engine(RetryingClient(), sink, blueprints=blueprints)

    own = [(t, f) for t, f in events if f.get("persona_index") == 2]
    assert [t for t, _ in own] == [
        "persona_started",
        "persona_retry",
        "persona_completed",
    ]
    assert all(f["persona_name"] == target.name for _, f in own)
    assert own[1][1]["attempt"] == 2
    assert own[1][1]["error_code"] == "RATE_LIMITED"
    completed = own[2][1]
    assert completed["attempt"] == 2
    assert (completed["input_tokens"], completed["output_tokens"]) == (10, 5)
    assert completed["duration_ms"] >= 0


def test_failed_persona_event_has_code_only() -> None:
    marker = "NYERS-SZOLGALTATOI-UZENET-42"

    class FailingClient:
        async def generate_json(
            self, *, system_prompt, user_prompt, temperature=0.3, on_retry=None
        ):
            raise LLMProviderError(error_code="UPSTREAM_ERROR", message=marker)

    events, sink = _collecting_sink()
    result = _run_engine(
        FailingClient(), sink, blueprints=build_persona_blueprints(total_personas=15)
    )

    failed = [f for t, f in events if t == "persona_failed"]
    assert len(failed) == 15
    assert all(f["error_code"] == "UPSTREAM_ERROR" and f["attempt"] == 1 for f in failed)
    assert all(
        (f["input_tokens"], f["output_tokens"]) == (0, 0) and f["duration_ms"] >= 0
        for f in failed
    )
    assert marker not in repr(events)
    assert marker not in repr([item.model_dump() for item in result.failures])


def test_personas_generated_event_only_when_generated() -> None:
    blueprints = [item.model_dump() for item in build_persona_blueprints(18)]

    class GeneratingClient:
        async def generate_json(
            self, *, system_prompt, user_prompt, temperature=0.3, on_retry=None
        ):
            if "Generálj" in user_prompt:
                return {"personas": blueprints}, TokenUsage(30, 20)
            return VALID_RESPONSE, TokenUsage(10, 5)

    preset_events, preset_sink = _collecting_sink()
    _run_engine(
        GeneratingClient(),
        preset_sink,
        blueprints=build_persona_blueprints(total_personas=18),
    )
    assert "personas_generated" not in [t for t, _ in preset_events]

    events, sink = _collecting_sink()
    result = _run_engine(GeneratingClient(), sink)
    generated = [f for t, f in events if t == "personas_generated"]
    assert len(generated) == 1
    assert (generated[0]["input_tokens"], generated[0]["output_tokens"]) == (30, 20)
    assert generated[0]["duration_ms"] >= 0
    assert events[0][0] == "personas_generated"
    assert (result.input_tokens, result.output_tokens) == (30 + 180, 20 + 90)


def test_sink_failure_does_not_stop_engine() -> None:
    class OkClient:
        async def generate_json(
            self, *, system_prompt, user_prompt, temperature=0.3, on_retry=None
        ):
            return VALID_RESPONSE, TokenUsage(10, 5)

    def broken_sink(type_: str, **fields) -> None:
        raise RuntimeError("az adatbázis nem érhető el")

    result = _run_engine(
        OkClient(), broken_sink, blueprints=build_persona_blueprints(total_personas=18)
    )
    assert len(result.responses) == 18


# --- blueprint-generátor -----------------------------------------------------


def _blueprint_client(count: int):
    base = build_persona_blueprints(18)[0].model_dump()
    items = [{**base, "name": f"P{i}"} for i in range(count)]

    class Client:
        async def generate_json(
            self, *, system_prompt, user_prompt, temperature=0.3, on_retry=None
        ):
            return {"personas": items}, TokenUsage(4, 2)

    return Client()


def _generate(client, count=18):
    return asyncio.run(
        generate_persona_blueprints(
            topic="Tema", audience="Kozonseg", count=count, llm_client=client
        )
    )


def test_extra_blueprints_are_truncated_to_count() -> None:
    blueprints, usage = _generate(_blueprint_client(20))
    assert len(blueprints) == 18
    assert usage == TokenUsage(4, 2)


def test_too_few_blueprints_raise() -> None:
    with pytest.raises(BlueprintGenerationError):
        _generate(_blueprint_client(17))


def test_provider_error_is_wrapped_with_usage() -> None:
    class Failing:
        async def generate_json(
            self, *, system_prompt, user_prompt, temperature=0.3, on_retry=None
        ):
            raise LLMProviderError(
                error_code="INVALID_JSON", message="x", usage=TokenUsage(7, 3)
            )

    with pytest.raises(BlueprintGenerationError) as excinfo:
        _generate(Failing())
    assert excinfo.value.usage == TokenUsage(7, 3)
    assert excinfo.value.__cause__ is None
