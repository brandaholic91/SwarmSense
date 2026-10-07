from __future__ import annotations

import hmac

from fastapi import Request

from app.core.config import get_settings
from app.core.errors import ErrorCode, error_response

PROTECTED_PREFIX = "/api/v1/runs"


def is_internal_endpoint(request: Request) -> bool:
    # minden /api/v1/runs és /api/v1/runs/... útvonal, metódustól függetlenül
    path = request.url.path.rstrip("/") or "/"
    return path == PROTECTED_PREFIX or path.startswith(PROTECTED_PREFIX + "/")


async def internal_auth_middleware(request: Request, call_next):
    if not is_internal_endpoint(request):
        return await call_next(request)

    settings = get_settings()
    secret = request.headers.get("X-Internal-Secret", "")
    # állandó idejű összehasonlítás; bájtokon, mert a str-változat nem-ASCII-ra hibázik
    if not secret or not hmac.compare_digest(
        secret.encode(), settings.internal_secret.encode()
    ):
        return error_response(
            status_code=401,
            detail="Unauthorized",
            code=ErrorCode.UNAUTHORIZED,
        )

    return await call_next(request)
