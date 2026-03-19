from __future__ import annotations

from datetime import date
from decimal import Decimal, InvalidOperation

from fastapi import Request

from app.core.database import get_supabase_client
from app.core.errors import ErrorCode, error_response

RUN_INITIATING_ENDPOINTS = {("POST", "/api/v1/runs")}
MONTHLY_CAP_USD = Decimal("50.00")


def _normalize_total(value: object) -> Decimal:
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError):
        return Decimal("0")


def _current_month() -> str:
    return date.today().strftime("%Y-%m")


def _fetch_month_total_usd() -> Decimal:
    supabase = get_supabase_client()
    month = _current_month()
    response = (
        supabase.table("cost_tracking").select("total_usd").eq("month", month).execute()
    )
    data = response.data or []
    if not data:
        return Decimal("0")
    return _normalize_total(data[0].get("total_usd", 0))


def is_run_initiating_request(request: Request) -> bool:
    return (request.method.upper(), request.url.path) in RUN_INITIATING_ENDPOINTS


async def cost_enforcement_middleware(request: Request, call_next):
    if not is_run_initiating_request(request):
        return await call_next(request)

    total_usd = _fetch_month_total_usd()
    if total_usd >= MONTHLY_CAP_USD:
        return error_response(
            status_code=402,
            detail="A havi ingyenes kapacitás elérte a határát.",
            code=ErrorCode.COST_LIMIT_REACHED,
        )

    return await call_next(request)
