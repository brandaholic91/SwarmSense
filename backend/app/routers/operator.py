from __future__ import annotations

import asyncio
import hmac
from decimal import Decimal, InvalidOperation
from datetime import datetime, timezone
from typing import Any, Literal, cast

from fastapi import APIRouter, HTTPException, Query, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.cost_enforcement import MONTHLY_CAP_USD as MONTHLY_API_CAP_USD, WARNING_THRESHOLD_PERCENT
from app.core.database import get_supabase_client
from app.core.config import get_settings
from app.models.operator import (
    DEFAULT_ERROR_CODE_FAILED,
    DEFAULT_ERROR_CODE_PARTIAL,
    OperatorQualifierResponseRow,
    OperatorQualifierResponsesResponse,
    OperatorCostResponse,
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

# Input validation limits
MAX_USER_IDS_PER_QUERY = 100
MAX_TEXT_FIELD_LENGTH = 500


def _require_valid_operator_credentials(
    credentials: HTTPAuthorizationCredentials | None,
) -> None:
    """Validate operator API key using constant-time comparison to prevent timing attacks."""
    settings = get_settings()
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden",
        )
    # Use constant-time comparison to prevent timing attacks
    if not hmac.compare_digest(credentials.credentials, settings.operator_api_key):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden",
        )


def _coerce_int(value: Any, field_name: str = "value") -> int:
    """Coerce value to int, rejecting invalid types to prevent silent data corruption."""
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    raise ValueError(
        f"Expected int or float for {field_name}, got {type(value).__name__}"
    )


def _coerce_float(value: Any, field_name: str = "value") -> float:
    """Coerce value to float, rejecting invalid types to prevent silent data corruption."""
    if isinstance(value, (int, float)):
        return float(value)
    raise ValueError(
        f"Expected numeric type for {field_name}, got {type(value).__name__}"
    )


def _extract_error_metadata(
    row: dict[str, Any],
    run_status: RunStatus,
) -> tuple[str | None, str | None]:
    """Extract error metadata from database row with fallback defaults for failed/partial runs.

    Searches multiple possible column names for error info to handle schema variations.
    For failed/partial runs without error metadata, generates default error codes and
    timestamps to ensure 100% coverage as required by AC3.
    """
    error_code: str | None = None
    error_at: str | None = None

    # Search for error code in various possible column names
    for key in ("error_code", "failure_code", "provider_error_code"):
        value = row.get(key)
        if isinstance(value, str) and value.strip():
            error_code = value.strip()
            break

    # Search for error timestamp in various possible column names
    for key in ("error_at", "failed_at", "error_timestamp"):
        value = row.get(key)
        if isinstance(value, str) and value.strip():
            error_at = value.strip()
            break

    # AC3: Ensure 100% error metadata coverage for failed/partial runs
    if run_status in {"failed", "partial"}:
        if error_code is None:
            error_code = (
                DEFAULT_ERROR_CODE_FAILED
                if run_status == "failed"
                else DEFAULT_ERROR_CODE_PARTIAL
            )
        if error_at is None:
            # Fallback to completed_at or created_at for error timestamp
            completed_at = row.get("completed_at")
            created_at = row.get("created_at")
            if isinstance(completed_at, str) and completed_at.strip():
                error_at = completed_at.strip()
            elif isinstance(created_at, str) and created_at.strip():
                error_at = created_at.strip()

    return error_code, error_at


def _load_user_email_by_user_id(
    *,
    supabase: Any,
    user_ids: list[str],
) -> dict[str, str]:
    """Load user emails by IDs with validation to prevent DoS via oversized queries."""
    if not user_ids:
        return {}

    # Validate and limit user_ids to prevent DoS
    if len(user_ids) > MAX_USER_IDS_PER_QUERY:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Too many user IDs requested. Maximum: {MAX_USER_IDS_PER_QUERY}",
        )

    try:
        user_result = (
            supabase.table("users").select("id,email").in_("id", user_ids).execute()
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to load operator runs",
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
    """Parse ISO datetime string and ensure timezone-aware result.

    Returns None for invalid formats. Assumes UTC if no timezone specified.
    """
    if value is None:
        return None
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        # Ensure timezone-aware datetime (AC requirement: AwareDatetime)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except ValueError:
        return None


def _load_run_user_by_run_id(
    *,
    supabase: Any,
    run_ids: list[str],
) -> dict[str, str]:
    """Load run owner mapping with validation to prevent oversized IN queries."""
    if not run_ids:
        return {}

    if len(run_ids) > MAX_USER_IDS_PER_QUERY:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Too many run IDs requested. Maximum: {MAX_USER_IDS_PER_QUERY}",
        )

    try:
        run_result = (
            supabase.table("runs").select("id,user_id").in_("id", run_ids).execute()
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to load qualifier responses",
        ) from exc

    run_rows = run_result.data or []
    return {
        cast(str, run_row["id"]): cast(str, run_row["user_id"])
        for run_row in run_rows
        if isinstance(run_row, dict)
        and isinstance(run_row.get("id"), str)
        and isinstance(run_row.get("user_id"), str)
    }


def _is_schema_error(exc: Exception) -> bool:
    """Check if exception is related to missing columns (schema mismatch)."""
    error_str = str(exc).lower()
    schema_error_indicators = [
        "column",
        "does not exist",
        "unknown column",
        "field",
        "schema",
    ]
    return any(indicator in error_str for indicator in schema_error_indicators)


def _validate_text_field(value: str, field_name: str) -> str:
    """Validate text field length to prevent oversized payloads."""
    if len(value) > MAX_TEXT_FIELD_LENGTH:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Field {field_name} exceeds maximum length",
        )
    return value


def _normalize_operator_cost_total(value: Any) -> Decimal:
    try:
        normalized = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to load operator cost",
        ) from exc

    if not normalized.is_finite() or normalized < 0:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to load operator cost",
        )
    return normalized


def _resolve_operator_cost_status(
    *, percentage: Decimal
) -> Literal["ok", "warning", "capped"]:
    if percentage >= Decimal("100"):
        return "capped"
    if percentage >= WARNING_THRESHOLD_PERCENT:
        return "warning"
    return "ok"


@router.get("/cost", response_model=OperatorCostResponse)
async def get_cost(
    credentials: HTTPAuthorizationCredentials | None = Security(_bearer),
) -> OperatorCostResponse:
    _require_valid_operator_credentials(credentials)

    month = datetime.now(timezone.utc).strftime("%Y-%m")
    supabase = get_supabase_client()

    try:
        result = (
            supabase.table("cost_tracking")
            .select("month,total_usd")
            .eq("month", month)
            .limit(1)
            .execute()
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to load operator cost",
        ) from exc

    rows = result.data or []
    total_usd = Decimal("0")
    if rows:
        row = rows[0]
        if not isinstance(row, dict):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to load operator cost",
            )
        total_usd = _normalize_operator_cost_total(row.get("total_usd", 0))

    percentage = (total_usd / MONTHLY_API_CAP_USD) * Decimal("100")
    status_value = _resolve_operator_cost_status(percentage=percentage)

    return OperatorCostResponse(
        month=month,
        total_usd=float(total_usd),
        cap_usd=float(MONTHLY_API_CAP_USD),
        percentage=float(percentage),
        status=status_value,
    )


@router.get("/qualifier-responses", response_model=OperatorQualifierResponsesResponse)
async def list_qualifier_responses(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    credentials: HTTPAuthorizationCredentials | None = Security(_bearer),
) -> OperatorQualifierResponsesResponse:
    """List qualifier survey responses with strict field exposure and auth."""
    _require_valid_operator_credentials(credentials)

    supabase = get_supabase_client()
    target_offset = (page - 1) * page_size
    scan_offset = 0
    scan_batch_size = page_size
    valid_total = 0
    items: list[OperatorQualifierResponseRow] = []

    while True:
        scan_limit_end = scan_offset + scan_batch_size - 1

        try:
            result = (
                supabase.table("qualifier_responses")
                .select("run_id,user_id,role_answer,use_case_answer,created_at")
                .order("created_at", desc=True)
                .range(scan_offset, scan_limit_end)
                .execute()
            )
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to load qualifier responses",
            ) from exc

        rows = result.data or []
        if not rows:
            break

        user_ids: list[str] = list(
            dict.fromkeys(
                cast(str, row["user_id"])
                for row in rows
                if isinstance(row, dict) and isinstance(row.get("user_id"), str)
            )
        )
        run_ids: list[str] = list(
            dict.fromkeys(
                cast(str, row["run_id"])
                for row in rows
                if isinstance(row, dict) and isinstance(row.get("run_id"), str)
            )
        )

        user_email_by_user_id = _load_user_email_by_user_id(
            supabase=supabase,
            user_ids=user_ids,
        )
        run_user_by_run_id = _load_run_user_by_run_id(
            supabase=supabase,
            run_ids=run_ids,
        )

        for row in rows:
            if not isinstance(row, dict):
                continue

            run_id = row.get("run_id")
            user_id = row.get("user_id")
            role_answer = row.get("role_answer")
            use_case_answer = row.get("use_case_answer")
            created_at_raw = row.get("created_at")

            if not (
                isinstance(run_id, str)
                and isinstance(user_id, str)
                and isinstance(role_answer, str)
                and isinstance(use_case_answer, str)
                and isinstance(created_at_raw, str)
            ):
                continue

            run_owner_user_id = run_user_by_run_id.get(run_id)
            user_email = user_email_by_user_id.get(user_id)
            if run_owner_user_id != user_id or user_email is None:
                continue

            created_at = _parse_iso_datetime(created_at_raw)
            if created_at is None:
                continue

            try:
                validated_role_answer = _validate_text_field(role_answer, "role_answer")
                validated_use_case_answer = _validate_text_field(
                    use_case_answer, "use_case_answer"
                )
            except HTTPException:
                continue

            if target_offset <= valid_total < target_offset + page_size:
                items.append(
                    OperatorQualifierResponseRow(
                        user_email=user_email,
                        role_answer=validated_role_answer,
                        use_case_answer=validated_use_case_answer,
                        created_at=created_at,
                    )
                )

            valid_total += 1

        scan_offset += len(rows)
        if len(rows) < scan_batch_size:
            break

    return OperatorQualifierResponsesResponse(
        page=page,
        page_size=page_size,
        total=valid_total,
        items=items,
    )


@router.get("/runs", response_model=OperatorRunsResponse)
async def list_runs(
    status_filter: RunStatus | None = Query(default=None, alias="status"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    credentials: HTTPAuthorizationCredentials | None = Security(_bearer),
) -> OperatorRunsResponse:
    """List operator runs with pagination, filtering, and error metadata.

    Returns paginated list of runs ordered by created_at descending.
    Supports filtering by status. All failed/partial runs include error metadata.
    """
    _require_valid_operator_credentials(credentials)

    supabase = get_supabase_client()
    offset = (page - 1) * page_size
    limit_end = offset + page_size - 1

    base_columns = "id,user_id,topic,audience,status,persona_count,cost_usd,created_at,completed_at"
    query_columns = f"{base_columns},error_code,error_at"

    query = supabase.table("runs").select(query_columns, count=cast(Any, "exact"))
    if status_filter is not None:
        query = query.eq("status", status_filter)

    try:
        result = query.order("created_at", desc=True).range(offset, limit_end).execute()
    except Exception as exc:
        # Only fallback on schema errors (missing columns), not other failures
        if not _is_schema_error(exc):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to load operator runs",
            ) from exc

        # Fallback: query without error columns for backward compatibility
        fallback_query = supabase.table("runs").select(
            base_columns, count=cast(Any, "exact")
        )
        if status_filter is not None:
            fallback_query = fallback_query.eq("status", status_filter)
        try:
            result = (
                fallback_query.order("created_at", desc=True)
                .range(offset, limit_end)
                .execute()
            )
        except Exception as fallback_exc:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to load operator runs",
            ) from fallback_exc

    rows = result.data or []
    total = int(result.count) if isinstance(result.count, int) else 0

    # Deduplicate user_ids before querying to avoid redundant lookups
    user_ids: list[str] = list(
        dict.fromkeys(
            cast(str, row["user_id"])
            for row in rows
            if isinstance(row, dict) and isinstance(row.get("user_id"), str)
        )
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
        run_status_raw = row.get("status")
        created_at = row.get("created_at")

        if not (
            isinstance(run_id, str)
            and isinstance(user_id, str)
            and isinstance(topic, str)
            and isinstance(audience, str)
            and isinstance(run_status_raw, str)
            and isinstance(created_at, str)
        ):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to load operator runs",
            )

        # Normalize status to lowercase for case-insensitive comparison
        run_status = run_status_raw.lower()
        if run_status not in _run_statuses:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to load operator runs",
            )

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
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to load operator runs",
            )

        # Validate and coerce numeric fields with proper error handling
        try:
            persona_count = _coerce_int(row.get("persona_count"), "persona_count")
            cost_usd = _coerce_float(row.get("cost_usd"), "cost_usd")
        except ValueError as ve:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Data validation error: {ve}",
            ) from ve

        # Validate text fields
        topic = _validate_text_field(topic, "topic")
        audience = _validate_text_field(audience, "audience")

        item = OperatorRunRow(
            run_id=run_id,
            user_email=user_email_by_user_id.get(user_id, "unknown@local"),
            topic=topic,
            audience=audience,
            status=typed_status,
            persona_count=persona_count,
            cost_usd=cost_usd,
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
    """Dispatch follow-up emails for pending runs."""
    _require_valid_operator_credentials(credentials)

    sent = await asyncio.to_thread(dispatch_followup_sequence)
    return SendFollowupsResponse(sent=sent)
