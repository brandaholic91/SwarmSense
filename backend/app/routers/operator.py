from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Any, Literal, cast

from fastapi import APIRouter, HTTPException, Query, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.database import get_supabase_client
from app.core.config import get_settings
from app.models.operator import (
    OperatorRunRow,
    OperatorRunsResponse,
    SendFollowupsResponse,
)
from app.services.email_service import dispatch_followup_sequence

router = APIRouter(prefix="/api/v1/operator", tags=["operator"])

_bearer = HTTPBearer(auto_error=False)
RunStatus = Literal["queued", "running", "composing", "completed", "partial", "failed"]
_run_statuses = frozenset(
    {"queued", "running", "composing", "completed", "partial", "failed"}
)


def _require_valid_operator_credentials(
    credentials: HTTPAuthorizationCredentials | None,
) -> None:
    settings = get_settings()
    if credentials is None or credentials.credentials != settings.operator_api_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden",
        )


def _coerce_int(value: Any) -> int:
    if isinstance(value, (int, float)):
        return int(value)
    return 0


def _coerce_float(value: Any) -> float:
    if isinstance(value, (int, float)):
        return float(value)
    return 0.0


def _extract_error_metadata(
    row: dict[str, Any],
    run_status: RunStatus,
) -> tuple[str | None, str | None]:
    error_code: str | None = None
    error_at: str | None = None

    for key in ("error_code", "failure_code", "provider_error_code"):
        value = row.get(key)
        if isinstance(value, str) and value:
            error_code = value
            break

    for key in ("error_at", "failed_at", "error_timestamp"):
        value = row.get(key)
        if isinstance(value, str) and value:
            error_at = value
            break

    if run_status in {"failed", "partial"}:
        if error_code is None:
            error_code = "RUN_FAILED" if run_status == "failed" else "RUN_PARTIAL"
        if error_at is None:
            completed_at = row.get("completed_at")
            created_at = row.get("created_at")
            if isinstance(completed_at, str) and completed_at:
                error_at = completed_at
            elif isinstance(created_at, str) and created_at:
                error_at = created_at

    return error_code, error_at


def _load_user_email_by_user_id(
    *,
    supabase: Any,
    user_ids: list[str],
) -> dict[str, str]:
    if not user_ids:
        return {}

    try:
        user_result = (
            supabase.table("users").select("id,email").in_("id", user_ids).execute()
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail="Failed to load operator runs"
        ) from exc

    user_rows = user_result.data or []
    user_email_by_user_id: dict[str, str] = {}
    for user_row in user_rows:
        if not isinstance(user_row, dict):
            continue
        user_id = user_row.get("id")
        user_email = user_row.get("email")
        if isinstance(user_id, str) and isinstance(user_email, str) and user_email:
            user_email_by_user_id[user_id] = user_email
    return user_email_by_user_id


def _parse_iso_datetime(value: str | None) -> datetime | None:
    if value is None:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


@router.get("/runs", response_model=OperatorRunsResponse)
async def list_runs(
    status_filter: RunStatus | None = Query(default=None, alias="status"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    credentials: HTTPAuthorizationCredentials | None = Security(_bearer),
) -> OperatorRunsResponse:
    _require_valid_operator_credentials(credentials)

    supabase = get_supabase_client()
    offset = (page - 1) * page_size
    limit_end = offset + page_size - 1

    base_columns = "id,user_id,topic,audience,status,persona_count,cost_usd,created_at,completed_at"
    query_columns = f"{base_columns},error_code,error_at"

    query = cast(Any, supabase.table("runs")).select(query_columns, count="exact")
    if status_filter is not None:
        query = query.eq("status", status_filter)

    try:
        result = query.order("created_at", desc=True).range(offset, limit_end).execute()
    except Exception:
        fallback_query = cast(Any, supabase.table("runs")).select(
            base_columns, count="exact"
        )
        if status_filter is not None:
            fallback_query = fallback_query.eq("status", status_filter)
        try:
            result = (
                fallback_query.order("created_at", desc=True)
                .range(offset, limit_end)
                .execute()
            )
        except Exception as exc:
            raise HTTPException(
                status_code=500, detail="Failed to load operator runs"
            ) from exc

    rows = result.data or []
    total = int(result.count) if isinstance(result.count, int) else 0

    user_ids = sorted(
        [
            row["user_id"]
            for row in rows
            if isinstance(row, dict) and isinstance(row.get("user_id"), str)
        ]
    )
    user_email_by_user_id = _load_user_email_by_user_id(
        supabase=supabase, user_ids=user_ids
    )

    items: list[OperatorRunRow] = []
    for row in rows:
        if not isinstance(row, dict):
            continue

        run_id = row.get("id")
        user_id = row.get("user_id")
        topic = row.get("topic")
        audience = row.get("audience")
        run_status = row.get("status")
        created_at = row.get("created_at")

        if not (
            isinstance(run_id, str)
            and isinstance(user_id, str)
            and isinstance(topic, str)
            and isinstance(audience, str)
            and isinstance(run_status, str)
            and run_status in _run_statuses
            and isinstance(created_at, str)
        ):
            raise HTTPException(status_code=500, detail="Failed to load operator runs")

        typed_status = cast(RunStatus, run_status)
        error_code, error_at = _extract_error_metadata(row, typed_status)

        created_at_dt = _parse_iso_datetime(created_at)
        completed_at_raw = row.get("completed_at")
        completed_at_dt = (
            _parse_iso_datetime(completed_at_raw)
            if isinstance(completed_at_raw, str)
            else None
        )
        error_at_dt = _parse_iso_datetime(error_at)
        if created_at_dt is None:
            raise HTTPException(status_code=500, detail="Failed to load operator runs")

        item = OperatorRunRow(
            run_id=run_id,
            user_email=user_email_by_user_id.get(user_id, "unknown@local"),
            topic=topic,
            audience=audience,
            status=typed_status,
            persona_count=_coerce_int(row.get("persona_count")),
            cost_usd=_coerce_float(row.get("cost_usd")),
            created_at=created_at_dt,
            completed_at=completed_at_dt,
            error_code=error_code,
            error_at=error_at_dt,
        )
        items.append(item)

    return OperatorRunsResponse(
        page=page, page_size=page_size, total=total, items=items
    )


@router.post("/send-followups", response_model=SendFollowupsResponse)
async def send_followups(
    credentials: HTTPAuthorizationCredentials | None = Security(_bearer),
) -> SendFollowupsResponse:
    _require_valid_operator_credentials(credentials)

    sent = await asyncio.to_thread(dispatch_followup_sequence)
    return SendFollowupsResponse(sent=sent)
