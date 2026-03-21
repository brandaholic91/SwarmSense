from __future__ import annotations

import asyncio
import json
from decimal import Decimal, InvalidOperation
from typing import Any, Awaitable, Callable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from app.core.config import get_settings


class LLMProviderError(Exception):
    def __init__(self, *, error_code: str, message: str) -> None:
        super().__init__(message)
        self.error_code = error_code


class TransportError(Exception):
    def __init__(self, *, status_code: int | None, body: dict[str, Any] | None) -> None:
        super().__init__(f"Transport error: status_code={status_code}")
        self.status_code = status_code
        self.body = body


TransportFn = Callable[
    [str, dict[str, str], dict[str, Any]],
    Awaitable[dict[str, Any]],
]


class OpenRouterClient:
    def __init__(
        self,
        *,
        transport: TransportFn | None = None,
        sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
        max_attempts: int = 3,
        base_backoff_seconds: float = 0.5,
    ) -> None:
        if max_attempts < 1:
            raise ValueError("max_attempts must be at least 1.")
        self._settings = get_settings()
        self._transport = transport or _post_json
        self._sleep = sleep
        self._max_attempts = max_attempts
        self._base_backoff_seconds = base_backoff_seconds

    async def generate_persona_response(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
    ) -> dict[str, Any]:
        response, _ = await self.generate_persona_response_with_meta(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
        )
        return response

    async def generate_persona_response_with_meta(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
    ) -> tuple[dict[str, Any], float]:
        if not self._settings.openrouter_api_key:
            raise LLMProviderError(
                error_code="OPENROUTER_MISSING_API_KEY",
                message="OpenRouter API key is not configured.",
            )

        payload = {
            "model": self._settings.openrouter_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.3,
            "response_format": {"type": "json_object"},
        }
        headers = {
            "Authorization": f"Bearer {self._settings.openrouter_api_key}",
            "Content-Type": "application/json",
        }
        endpoint = (
            f"{str(self._settings.openrouter_base_url).rstrip('/')}/chat/completions"
        )

        raw = await self._request_with_retry(
            endpoint=endpoint, headers=headers, payload=payload
        )
        return _extract_json_content(raw), _extract_cost_usd(raw)

    async def _request_with_retry(
        self,
        *,
        endpoint: str,
        headers: dict[str, str],
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        last_error: TransportError | None = None

        for attempt in range(1, self._max_attempts + 1):
            try:
                return await self._transport(endpoint, headers, payload)
            except TransportError as exc:
                last_error = exc
                if not _is_retryable(exc.status_code) or attempt >= self._max_attempts:
                    break
                backoff_seconds = self._base_backoff_seconds * (2 ** (attempt - 1))
                await self._sleep(backoff_seconds)

        if last_error is None:
            raise LLMProviderError(
                error_code="OPENROUTER_REQUEST_FAILED",
                message="No transport attempts were made.",
            )
        raise LLMProviderError(
            error_code=_classify_error_code(last_error.status_code),
            message=_build_provider_error_message(last_error),
        )


async def _post_json(
    url: str,
    headers: dict[str, str],
    payload: dict[str, Any],
) -> dict[str, Any]:
    return await asyncio.to_thread(_post_json_sync, url, headers, payload)


def _post_json_sync(
    url: str,
    headers: dict[str, str],
    payload: dict[str, Any],
) -> dict[str, Any]:
    data = json.dumps(payload).encode("utf-8")
    request = Request(url=url, data=data, headers=headers, method="POST")

    try:
        with urlopen(request, timeout=60) as response:
            body = response.read().decode("utf-8")
            return json.loads(body)
    except HTTPError as exc:
        body_text = exc.read().decode("utf-8", errors="replace")
        parsed_body = _parse_error_body(body_text)
        raise TransportError(status_code=exc.code, body=parsed_body) from exc
    except URLError as exc:
        raise TransportError(
            status_code=None, body={"detail": str(exc.reason)}
        ) from exc


def _parse_error_body(raw_body: str) -> dict[str, Any] | None:
    if not raw_body:
        return None
    try:
        parsed = json.loads(raw_body)
    except json.JSONDecodeError:
        return {"detail": raw_body}
    return parsed if isinstance(parsed, dict) else {"detail": str(parsed)}


def _extract_json_content(payload: dict[str, Any]) -> dict[str, Any]:
    choices = payload.get("choices")
    if not isinstance(choices, list) or not choices:
        raise LLMProviderError(
            error_code="OPENROUTER_INVALID_RESPONSE",
            message="OpenRouter response does not contain choices.",
        )

    first_choice = choices[0]
    if not isinstance(first_choice, dict):
        raise LLMProviderError(
            error_code="OPENROUTER_INVALID_RESPONSE",
            message="OpenRouter response contains invalid choice payload.",
        )

    message = first_choice.get("message")
    if not isinstance(message, dict):
        raise LLMProviderError(
            error_code="OPENROUTER_INVALID_RESPONSE",
            message="OpenRouter response does not contain message payload.",
        )

    content = message.get("content")
    if isinstance(content, dict):
        return content
    if isinstance(content, list):
        joined = "".join(_extract_content_fragment(item) for item in content)
        return _loads_content(joined)
    if isinstance(content, str):
        return _loads_content(content)

    raise LLMProviderError(
        error_code="OPENROUTER_INVALID_RESPONSE",
        message="OpenRouter response content is missing.",
    )


def _extract_content_fragment(fragment: Any) -> str:
    if isinstance(fragment, str):
        return fragment
    if isinstance(fragment, dict):
        text = fragment.get("text")
        if isinstance(text, str):
            return text
    return ""


def _loads_content(content: str) -> dict[str, Any]:
    try:
        parsed = json.loads(content)
    except json.JSONDecodeError as exc:
        raise LLMProviderError(
            error_code="OPENROUTER_INVALID_JSON",
            message="Provider content is not valid JSON.",
        ) from exc
    if not isinstance(parsed, dict):
        raise LLMProviderError(
            error_code="OPENROUTER_INVALID_JSON",
            message="Provider content JSON must be an object.",
        )
    return parsed


def _is_retryable(status_code: int | None) -> bool:
    if status_code == 429:
        return True
    if status_code is None:
        return True
    return 500 <= status_code < 600


def _classify_error_code(status_code: int | None) -> str:
    if status_code == 429:
        return "OPENROUTER_RATE_LIMIT"
    if status_code is None:
        return "OPENROUTER_NETWORK_ERROR"
    if 500 <= status_code < 600:
        return "OPENROUTER_UPSTREAM_ERROR"
    return "OPENROUTER_REQUEST_FAILED"


def _build_provider_error_message(error: TransportError) -> str:
    if error.body:
        detail = error.body.get("error") or error.body.get("detail")
        if isinstance(detail, str) and detail.strip():
            return detail
    if error.status_code is not None:
        return f"OpenRouter request failed with status {error.status_code}."
    return "OpenRouter request failed because of a network error."


def _extract_cost_usd(payload: dict[str, Any]) -> float:
    usage = payload.get("usage")
    if not isinstance(usage, dict):
        return 0.0

    for key in ("cost", "total_cost", "cost_usd"):
        value = usage.get(key)
        if value is None:
            continue
        try:
            normalized = Decimal(str(value))
        except (InvalidOperation, TypeError, ValueError):
            continue
        if normalized < 0:
            return 0.0
        return float(normalized)

    return 0.0
