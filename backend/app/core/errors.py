from __future__ import annotations

from enum import Enum

from fastapi.responses import JSONResponse


class ErrorCode(str, Enum):
    COST_LIMIT_REACHED = "COST_LIMIT_REACHED"
    COST_CHECK_FAILED = "COST_CHECK_FAILED"
    UNAUTHORIZED = "UNAUTHORIZED"
    RUN_NOT_FOUND = "RUN_NOT_FOUND"


def error_response(status_code: int, detail: str, code: ErrorCode) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"detail": detail, "code": code.value},
    )
