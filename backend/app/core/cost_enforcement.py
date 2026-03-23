from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation
from typing import Any, cast

from fastapi import Request

from app.core.database import get_supabase_client
from app.core.errors import ErrorCode, error_response

RUN_INITIATING_ENDPOINTS = {("POST", "/api/v1/runs"), ("POST", "/api/v1/run-sessions")}
MONTHLY_CAP_USD = Decimal("50.00")


class CostCheckError(Exception):
    pass


def _normalize_total(value: object) -> Decimal:
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError) as exc:
        raise CostCheckError(
            f"Invalid total_usd value in cost_tracking: {value!r}"
        ) from exc


def _current_month() -> str:
    return datetime.now(UTC).strftime("%Y-%m")


async def _fetch_month_total_usd() -> Decimal:
    try:
        supabase = get_supabase_client()
        month = _current_month()
        response = await asyncio.to_thread(
            lambda: supabase.table("cost_tracking")
            .select("total_usd")
            .eq("month", month)
            .limit(1)
            .execute()
        )
        data = response.data or []
        if not data:
            return Decimal("0")
        row = data[0]
        if not isinstance(row, dict):
            raise CostCheckError("Invalid cost_tracking row payload")
        row_payload = cast(dict[str, Any], row)
        return _normalize_total(row_payload.get("total_usd", 0))
    except CostCheckError:
        raise
    except Exception as exc:
        raise CostCheckError("Failed to fetch monthly cost total") from exc


def is_run_initiating_request(request: Request) -> bool:
    path = request.url.path.rstrip("/") or "/"
    return (request.method.upper(), path) in RUN_INITIATING_ENDPOINTS


async def cost_enforcement_middleware(request: Request, call_next):
    if not is_run_initiating_request(request):
        return await call_next(request)

    try:
        total_usd = await _fetch_month_total_usd()
    except CostCheckError:
        return error_response(
            status_code=503,
            detail="Nem sikerült ellenőrizni a havi költségkeretet.",
            code=ErrorCode.COST_CHECK_FAILED,
        )

    if total_usd >= MONTHLY_CAP_USD:
        return error_response(
            status_code=402,
            detail="A havi ingyenes kapacitás elérte a határát.",
            code=ErrorCode.COST_LIMIT_REACHED,
        )

    return await call_next(request)
