from __future__ import annotations

import asyncio

import pytest

from app.services.llm_client import (
    LLMClient,
    LLMProviderError,
    TokenUsage,
    TransportError,
)

PERSONA_JSON = '{"name":"A","role":"B","stance":"support","primary_argument":"C","change_condition":"D"}'


def test_request_shape():
    seen = {}

    async def fake_transport(url, headers, payload):
        seen.update(url=url, headers=headers, payload=payload)
        return {
            "choices": [{"message": {"content": '{"ok": true}', "reasoning_content": "..."}}],
            "usage": {"prompt_tokens": 79, "completion_tokens": 74, "total_tokens": 153},
        }

    client = LLMClient(session_id="swarmsense-run-1", transport=fake_transport)
    data, usage = asyncio.run(client.generate_json(system_prompt="s", user_prompt="u"))

    assert seen["url"] == "https://opencode.ai/zen/go/v1/chat/completions"
    assert seen["headers"]["x-opencode-session"] == "swarmsense-run-1"
    assert seen["headers"]["User-Agent"] == "swarmsense/0.1"
    assert seen["headers"]["Authorization"] == "Bearer test-llm-key"
    assert seen["payload"]["model"] == "deepseek-v4.1-flash"
    assert seen["payload"]["response_format"] == {"type": "json_object"}
    assert data == {"ok": True}
    assert usage == TokenUsage(input_tokens=79, output_tokens=74)


@pytest.mark.parametrize(
    "usage",
    [
        None,
        {},
        {"prompt_tokens": None},
        {"prompt_tokens": "x"},
        {"prompt_tokens": -5, "completion_tokens": -1},
        {"prompt_tokens": 1.5, "completion_tokens": 2.0},
        {"prompt_tokens": True, "completion_tokens": False},
        "nem objektum",
    ],
)
def test_missing_or_malformed_usage_gives_zero_tokens(usage):
    async def fake_transport(url, headers, payload):
        body = {"choices": [{"message": {"content": '{"ok": true}'}}]}
        if usage is not None:
            body["usage"] = usage
        return body

    client = LLMClient(session_id="s", transport=fake_transport)
    _, tokens = asyncio.run(client.generate_json(system_prompt="s", user_prompt="u"))
    assert tokens == TokenUsage(0, 0)


def test_valid_field_counted_invalid_field_zero():
    async def fake_transport(url, headers, payload):
        return {
            "choices": [{"message": {"content": '{"ok": true}'}}],
            "usage": {"prompt_tokens": 42, "completion_tokens": "x"},
        }

    client = LLMClient(session_id="s", transport=fake_transport)
    _, tokens = asyncio.run(client.generate_json(system_prompt="s", user_prompt="u"))
    assert tokens == TokenUsage(42, 0)


def test_invalid_json_error_carries_usage():
    async def fake_transport(url, headers, payload):
        return {
            "choices": [{"message": {"content": "nem json"}}],
            "usage": {"prompt_tokens": 7, "completion_tokens": 3},
        }

    client = LLMClient(session_id="s", transport=fake_transport)
    with pytest.raises(LLMProviderError) as exc_info:
        asyncio.run(client.generate_json(system_prompt="s", user_prompt="u"))

    assert exc_info.value.error_code == "INVALID_JSON"
    assert exc_info.value.usage == TokenUsage(7, 3)


def test_token_usage_adds():
    assert TokenUsage(1, 2) + TokenUsage(10, 20) == TokenUsage(11, 22)


def test_retries_rate_limit_three_attempts() -> None:
    attempts = {"count": 0}
    sleeps: list[float] = []

    async def fake_transport(_url, _headers, _payload):
        attempts["count"] += 1
        raise TransportError(status_code=429, body={"detail": "too many requests"})

    async def fake_sleep(seconds: float) -> None:
        sleeps.append(seconds)

    client = LLMClient(session_id="s", transport=fake_transport, sleep=fake_sleep)

    with pytest.raises(LLMProviderError) as exc_info:
        asyncio.run(client.generate_json(system_prompt="system", user_prompt="user"))

    assert attempts["count"] == 3
    assert sleeps == [0.5, 1.0]
    assert exc_info.value.error_code == "RATE_LIMITED"


def test_terminal_failure_classification() -> None:
    attempts = {"count": 0}

    async def fake_transport(_url, _headers, _payload):
        attempts["count"] += 1
        raise TransportError(status_code=400, body={"detail": "bad request"})

    client = LLMClient(session_id="s", transport=fake_transport)

    with pytest.raises(LLMProviderError) as exc_info:
        asyncio.run(client.generate_json(system_prompt="system", user_prompt="user"))

    assert attempts["count"] == 1
    assert exc_info.value.error_code == "REQUEST_FAILED"


def test_extracts_json_object_from_mixed_content() -> None:
    async def fake_transport(_url, _headers, _payload):
        return {
            "choices": [
                {
                    "message": {
                        "content": (
                            "Megjegyzes: az alabbi valasz JSON.\n"
                            + PERSONA_JSON
                            + "\nUtolso sor: kesz."
                        )
                    }
                }
            ]
        }

    client = LLMClient(session_id="s", transport=fake_transport)
    response, _ = asyncio.run(
        client.generate_json(system_prompt="system", user_prompt="user")
    )

    assert response["name"] == "A"
    assert response["stance"] == "support"
