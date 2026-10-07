from __future__ import annotations

from enum import Enum

from fastapi.responses import JSONResponse


class ErrorCode(str, Enum):
    UNAUTHORIZED = "UNAUTHORIZED"
    RUN_NOT_FOUND = "RUN_NOT_FOUND"
    RUN_START_FAILED = "RUN_START_FAILED"
    BUSY = "BUSY"
    IP_LIMIT_REACHED = "IP_LIMIT_REACHED"
    DAILY_LIMIT_REACHED = "DAILY_LIMIT_REACHED"


def error_response(status_code: int, detail: str, code: ErrorCode) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"detail": detail, "code": code.value},
    )
