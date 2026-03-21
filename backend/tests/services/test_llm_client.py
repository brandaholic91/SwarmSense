from __future__ import annotations

import asyncio

import pytest

from app.core.config import get_settings
from app.services.llm_client import LLMProviderError, OpenRouterClient, TransportError


def _seed_openrouter_env(monkeypatch) -> None:
    monkeypatch.setenv("SWARMSENSE_SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setenv("SWARMSENSE_SUPABASE_SERVICE_KEY", "service-key")
    monkeypatch.setenv("SWARMSENSE_KIMI_API_KEY", "kimi-key")
    monkeypatch.setenv("SWARMSENSE_OPERATOR_API_KEY", "operator-key")
    monkeypatch.setenv("SWARMSENSE_INTERNAL_SECRET", "test-internal-secret")
    monkeypatch.setenv("SWARMSENSE_FRONTEND_ORIGIN", "https://swarmsense.vercel.app")
    monkeypatch.setenv("SWARMSENSE_RESEND_API_KEY", "re_test")
    monkeypatch.setenv("SWARMSENSE_OPENROUTER_API_KEY", "or_test")
    monkeypatch.setenv("SWARMSENSE_OPENROUTER_MODEL", "moonshotai/kimi-k2")
    monkeypatch.setenv("SWARMSENSE_OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    get_settings.cache_clear()


def test_openrouter_request_shape(monkeypatch) -> None:
    _seed_openrouter_env(monkeypatch)
    captured: dict[str, object] = {}

    async def fake_transport(
        url: str, headers: dict[str, str], payload: dict[str, object]
    ):
        captured["url"] = url
        captured["headers"] = headers
        captured["payload"] = payload
        return {
            "choices": [
                {
                    "message": {
                        "content": '{"name":"A","role":"B","stance":"support","primary_argument":"C","change_condition":"D"}'
                    }
                }
            ]
        }

    client = OpenRouterClient(transport=fake_transport)
    response = asyncio.run(
        client.generate_persona_response(
            system_prompt="system",
            user_prompt="user",
        )
    )

    assert response["stance"] == "support"
    assert str(captured["url"]).endswith("/chat/completions")
    headers = captured["headers"]
    assert isinstance(headers, dict)
    assert headers["Authorization"].startswith("Bearer ")
    payload = captured["payload"]
    assert isinstance(payload, dict)
    assert payload["model"] == "moonshotai/kimi-k2"


def test_retries_rate_limit_three_attempts(monkeypatch) -> None:
    _seed_openrouter_env(monkeypatch)
    attempts = {"count": 0}
    sleeps: list[float] = []

    async def fake_transport(
        _url: str, _headers: dict[str, str], _payload: dict[str, object]
    ):
        attempts["count"] += 1
        raise TransportError(status_code=429, body={"detail": "too many requests"})

    async def fake_sleep(seconds: float) -> None:
        sleeps.append(seconds)

    client = OpenRouterClient(transport=fake_transport, sleep=fake_sleep)

    with pytest.raises(LLMProviderError) as exc_info:
        asyncio.run(
            client.generate_persona_response(
                system_prompt="system",
                user_prompt="user",
            )
        )

    assert attempts["count"] == 3
    assert sleeps == [0.5, 1.0]
    assert exc_info.value.error_code == "OPENROUTER_RATE_LIMIT"


def test_terminal_failure_classification(monkeypatch) -> None:
    _seed_openrouter_env(monkeypatch)

    async def fake_transport(
        _url: str, _headers: dict[str, str], _payload: dict[str, object]
    ):
        raise TransportError(status_code=400, body={"detail": "bad request"})

    client = OpenRouterClient(transport=fake_transport)

    with pytest.raises(LLMProviderError) as exc_info:
        asyncio.run(
            client.generate_persona_response(
                system_prompt="system",
                user_prompt="user",
            )
        )

    assert exc_info.value.error_code == "OPENROUTER_REQUEST_FAILED"
