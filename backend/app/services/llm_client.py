from __future__ import annotations

import asyncio
import http.client
import json
from dataclasses import dataclass
from typing import Any, Awaitable, Callable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from app.core.config import get_settings


USER_AGENT = "swarmsense/0.1"


@dataclass(frozen=True)
class TokenUsage:
    input_tokens: int = 0
    output_tokens: int = 0

    def __add__(self, other: TokenUsage) -> TokenUsage:
        return TokenUsage(
            input_tokens=self.input_tokens + other.input_tokens,
            output_tokens=self.output_tokens + other.output_tokens,
        )


class LLMProviderError(Exception):
    def __init__(
        self, *, error_code: str, message: str, usage: TokenUsage | None = None
    ) -> None:
        super().__init__(message)
        self.error_code = error_code
        # a hívás tokenjei, ha a szolgáltató válaszolt, de a válasz használhatatlan
        self.usage = usage or TokenUsage()


class TransportError(Exception):
    def __init__(self, *, status_code: int | None, body: dict[str, Any] | None) -> None:
        super().__init__(f"Transport error: status_code={status_code}")
        self.status_code = status_code
        self.body = body


TransportFn = Callable[
    [str, dict[str, str], dict[str, Any]],
    Awaitable[dict[str, Any]],
]


class LLMClient:
    def __init__(
        self,
        *,
        session_id: str,
        transport: TransportFn | None = None,
        sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
        max_attempts: int = 3,
        base_backoff_seconds: float = 0.5,
    ) -> None:
        if max_attempts < 1:
            raise ValueError("max_attempts must be at least 1.")
        self._settings = get_settings()
        self._session_id = session_id
        self._transport = transport or _post_json
        self._sleep = sleep
        self._max_attempts = max_attempts
        self._base_backoff_seconds = base_backoff_seconds

    async def generate_json(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.3,
    ) -> tuple[dict[str, Any], TokenUsage]:
        if not self._settings.llm_api_key:
            raise LLMProviderError(
                error_code="MISSING_API_KEY",
                message="LLM API key is not configured.",
            )

        payload = {
            "model": self._settings.llm_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": temperature,
            "response_format": {"type": "json_object"},
        }
        headers = {
            "Authorization": f"Bearer {self._settings.llm_api_key}",
            "Content-Type": "application/json",
            "x-opencode-session": self._session_id,
            "User-Agent": USER_AGENT,
        }
        endpoint = (
            f"{str(self._settings.llm_base_url).rstrip('/')}/chat/completions"
        )

        raw = await self._request_with_retry(
            endpoint=endpoint, headers=headers, payload=payload
        )
        usage = _extract_usage(raw)
        try:
            return _extract_json_content(raw), usage
        except LLMProviderError as exc:
            exc.usage = usage
            raise

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
                error_code="REQUEST_FAILED",
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
    except (OSError, http.client.HTTPException, json.JSONDecodeError) as exc:
        # timeout, kapcsolat-megszakadás, félbemaradt vagy nem JSON válasz:
        # a nyers kivételszöveg nem kerül a body-ba, csak a típus neve
        raise TransportError(
            status_code=None, body={"detail": type(exc).__name__}
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
            error_code="INVALID_RESPONSE",
            message="LLM response does not contain choices.",
        )

    first_choice = choices[0]
    if not isinstance(first_choice, dict):
        raise LLMProviderError(
            error_code="INVALID_RESPONSE",
            message="LLM response contains invalid choice payload.",
        )

    message = first_choice.get("message")
    if not isinstance(message, dict):
        raise LLMProviderError(
            error_code="INVALID_RESPONSE",
            message="LLM response does not contain message payload.",
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
        error_code="INVALID_RESPONSE",
        message="LLM response content is missing.",
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
        parsed = _extract_first_json_object(content)
        if parsed is None:
            raise LLMProviderError(
                error_code="INVALID_JSON",
                message="Provider content is not valid JSON.",
            ) from exc
    if not isinstance(parsed, dict):
        raise LLMProviderError(
            error_code="INVALID_JSON",
            message="Provider content JSON must be an object.",
        )
    return parsed


def _extract_first_json_object(content: str) -> dict[str, Any] | None:
    decoder = json.JSONDecoder()
    for idx, char in enumerate(content):
        if char != "{":
            continue
        try:
            parsed, _end = decoder.raw_decode(content[idx:])
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            return parsed
    return None


def _is_retryable(status_code: int | None) -> bool:
    if status_code == 429:
        return True
    if status_code is None:
        return True
    return 500 <= status_code < 600


def _classify_error_code(status_code: int | None) -> str:
    if status_code == 429:
        return "RATE_LIMITED"
    if status_code is None:
        return "NETWORK_ERROR"
    if 500 <= status_code < 600:
        return "UPSTREAM_ERROR"
    return "REQUEST_FAILED"


def _build_provider_error_message(error: TransportError) -> str:
    if error.body:
        detail = error.body.get("error") or error.body.get("detail")
        if isinstance(detail, str) and detail.strip():
            return detail
    if error.status_code is not None:
        return f"LLM request failed with status {error.status_code}."
    return "LLM request failed because of a network error."


def _extract_usage(payload: dict[str, Any]) -> TokenUsage:
    usage = payload.get("usage")
    if not isinstance(usage, dict):
        return TokenUsage()
    return TokenUsage(
        input_tokens=_token_count(usage.get("prompt_tokens")),
        output_tokens=_token_count(usage.get("completion_tokens")),
    )


def _token_count(value: Any) -> int:
    # bool az int alosztálya, de nem token-szám
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        return 0
    return value
