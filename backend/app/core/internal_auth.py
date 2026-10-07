from __future__ import annotations

from fastapi import Request

from app.core.config import get_settings
from app.core.errors import ErrorCode, error_response

INTERNAL_ONLY_ENDPOINTS = {
    ("POST", "/api/v1/runs"),
}


def is_internal_endpoint(request: Request) -> bool:
    path = request.url.path.rstrip("/") or "/"
    return (request.method.upper(), path) in INTERNAL_ONLY_ENDPOINTS


async def internal_auth_middleware(request: Request, call_next):
    if not is_internal_endpoint(request):
        return await call_next(request)

    settings = get_settings()
    secret = request.headers.get("X-Internal-Secret", "")
    if not secret or secret != settings.internal_secret:
        return error_response(
            status_code=401,
            detail="Unauthorized",
            code=ErrorCode.UNAUTHORIZED,
        )

    return await call_next(request)
