from __future__ import annotations

import logging
import math
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from threading import Lock
from typing import Any

import resend
import sentry_sdk

from app.core.config import get_settings
from app.models.operator import OperatorEmailStatsResponse

logger = logging.getLogger(__name__)

DELIVERY_ALERT_THRESHOLD = 0.95
DEFAULT_WINDOW_DAYS = 7
_RESEND_PAGE_SIZE = 100
_RESEND_MAX_PAGES = 10  # hard cap: 1 000 emails per request

_TRACKED_EMAIL_TYPES = frozenset(
    {
        "result",
        "magic_link",
        "followup_day1",
        "followup_day3",
        "followup_day7",
    }
)
_SUCCESS_EVENTS = frozenset({"delivered", "opened", "clicked"})
_OPEN_EVENTS = frozenset({"opened", "clicked"})

# Alert dedup state — bucket precision at 2 decimal places prevents oscillation
# between e.g. 0.9400/0.9401 from triggering repeated alerts.
_alert_state_lock = Lock()
_last_alert_bucket: float | None = None

# Thread-safe one-time Resend API key initialization
_resend_init_lock = Lock()
_resend_initialized = False


@dataclass
class _EmailTypeCounter:
    sent: int = 0
    delivered: int = 0
    opened: int = 0


def _ensure_resend_initialized() -> None:
    """Initialize resend.api_key exactly once to avoid unsafe concurrent global writes."""
    global _resend_initialized
    if _resend_initialized:
        return
    with _resend_init_lock:
        if _resend_initialized:
            return
        resend.api_key = get_settings().resend_api_key
        _resend_initialized = True


def _parse_iso_datetime(value: object) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=UTC)
    return dt


def _safe_int(value: object) -> int:
    """Convert API value to a non-negative int; NaN/Inf and negatives return 0."""
    if isinstance(value, bool):
        return 0
    if isinstance(value, float):
        if math.isnan(value) or math.isinf(value):
            return 0
        return max(0, int(value))
    if isinstance(value, int):
        return max(0, value)
    if isinstance(value, str):
        stripped = value.strip()
        if stripped.isdigit():
            return int(stripped)
    return 0


def _extract_tags(email_row: dict[str, Any]) -> dict[str, str]:
    tags_raw = email_row.get("tags")
    tags: dict[str, str] = {}
    if not isinstance(tags_raw, list):
        return tags

    for item in tags_raw:
        if not isinstance(item, dict):
            continue
        name = item.get("name")
        value = item.get("value")
        if not isinstance(name, str) or not isinstance(value, str):
            continue
        tags[name.strip().lower()] = value.strip().lower()
    return tags


def _resolve_email_type(email_row: dict[str, Any]) -> str | None:
    tags = _extract_tags(email_row)
    tagged_type = tags.get("email_type")
    if tagged_type in _TRACKED_EMAIL_TYPES:
        return tagged_type

    # Tag missing — fall back to subject heuristics (Hungarian subject lines).
    # This path should only occur for emails sent before email_type tagging was
    # introduced. Log a warning so systematic tagging failures are detectable.
    subject_raw = email_row.get("subject")
    subject = subject_raw.lower() if isinstance(subject_raw, str) else ""
    email_id = email_row.get("id", "<unknown>")

    resolved: str | None = None
    if "bejelentkez" in subject:
        resolved = "magic_link"
    elif "elemz" in subject and "elkesz" in subject:
        resolved = "result"
    elif "24 óra" in subject or "24 ora" in subject:
        # Require more specific phrase to avoid matching any subject with "24"
        resolved = "followup_day1"
    elif "het" in subject and "egy" not in subject:
        resolved = "followup_day3"
    elif "egy h" in subject:
        resolved = "followup_day7"

    if resolved is None:
        logger.warning(
            "email_metrics: could not resolve email type for id=%s subject=%r tags=%r",
            email_id,
            subject_raw,
            tags,
        )
    return resolved


def _is_delivered(email_row: dict[str, Any]) -> bool:
    last_event = email_row.get("last_event")
    if isinstance(last_event, str) and last_event.strip().lower() in _SUCCESS_EVENTS:
        return True

    # Only treat delivered_at as proof of delivery if it is a parseable datetime;
    # sentinel strings like "null" or "N/A" must not count.
    delivered_at = email_row.get("delivered_at")
    if _parse_iso_datetime(delivered_at) is not None:
        return True

    event_counts = email_row.get("event_counts")
    if isinstance(event_counts, dict):
        if _safe_int(event_counts.get("delivered")) > 0:
            return True
    return False


def _is_opened(email_row: dict[str, Any]) -> bool:
    last_event = email_row.get("last_event")
    if isinstance(last_event, str) and last_event.strip().lower() in _OPEN_EVENTS:
        return True

    if _safe_int(email_row.get("opens")) > 0:
        return True

    return _safe_int(email_row.get("open_count")) > 0


def _delivery_rate(*, sent: int, delivered: int) -> float:
    if sent <= 0:
        return 0.0
    return delivered / sent


def _open_rate(*, delivered: int, opened: int) -> float:
    """Open rate = opens / delivered (industry-standard denominator)."""
    if delivered <= 0:
        return 0.0
    return opened / delivered


def _load_resend_emails() -> list[dict[str, Any]]:
    """Fetch all emails from Resend via cursor-based pagination (up to _RESEND_MAX_PAGES pages)."""
    _ensure_resend_initialized()
    rows: list[dict[str, Any]] = []
    cursor: str | None = None

    for _ in range(_RESEND_MAX_PAGES):
        params: dict[str, Any] = {"limit": _RESEND_PAGE_SIZE}
        if cursor:
            params["starting_after"] = cursor

        try:
            result = resend.Emails.list(params=params)
        except TypeError:
            result = resend.Emails.list()

        page_rows: list[dict[str, Any]] = []
        next_cursor: str | None = None

        if isinstance(result, dict):
            data = result.get("data")
            if isinstance(data, list):
                page_rows = [item for item in data if isinstance(item, dict)]
            raw_next = result.get("next")
            if isinstance(raw_next, str) and raw_next.strip():
                next_cursor = raw_next.strip()
        elif isinstance(result, list):
            page_rows = [item for item in result if isinstance(item, dict)]

        rows.extend(page_rows)

        if not next_cursor or len(page_rows) < _RESEND_PAGE_SIZE:
            break
        cursor = next_cursor

    return rows


def _emit_delivery_health_alert_if_needed(
    *,
    rate: float,
    window_days: int,
    total_sent: int,
) -> None:
    global _last_alert_bucket

    # Do not alert on an empty sending window — zeroed rate is not a degradation.
    if total_sent <= 0:
        return

    if rate >= DELIVERY_ALERT_THRESHOLD:
        with _alert_state_lock:
            _last_alert_bucket = None
        return

    # Bucket at 2 decimal precision prevents alert storms from minor oscillations
    # (e.g. 0.9400 ↔ 0.9401 due to a single new email) without masking real shifts.
    current_bucket = round(rate, 2)
    with _alert_state_lock:
        if _last_alert_bucket == current_bucket:
            return
        prev_bucket = _last_alert_bucket
        _last_alert_bucket = current_bucket

    # Emit the Sentry alert; restore previous bucket on failure so the next call
    # can retry rather than being silently suppressed forever.
    try:
        with sentry_sdk.new_scope() as scope:
            scope.set_tag("alert_type", "email_delivery_rate_degraded")
            scope.set_tag("threshold", "95_percent")
            scope.set_extra("window_days", window_days)
            scope.set_extra("overall_delivery_rate", rate)
            scope.set_extra("total_sent", total_sent)
            sentry_sdk.capture_message(
                (
                    f"{window_days}-day email delivery success rate dropped below 95%: "
                    f"rate={rate:.4f}, sent={total_sent}"
                ),
                level="warning",
            )
    except Exception:
        with _alert_state_lock:
            _last_alert_bucket = prev_bucket


def reset_email_delivery_alert_state_for_tests() -> None:
    global _last_alert_bucket
    with _alert_state_lock:
        _last_alert_bucket = None


def get_email_stats_summary(
    *, window_days: int = DEFAULT_WINDOW_DAYS
) -> OperatorEmailStatsResponse:
    counters: dict[str, _EmailTypeCounter] = {
        "result": _EmailTypeCounter(),
        "magic_link": _EmailTypeCounter(),
        "followup_day1": _EmailTypeCounter(),
        "followup_day3": _EmailTypeCounter(),
        "followup_day7": _EmailTypeCounter(),
    }

    try:
        rows = _load_resend_emails()
    except Exception as exc:
        with sentry_sdk.new_scope() as scope:
            scope.set_tag("error_code", "EMAIL_METRICS_FETCH_FAILED")
            scope.set_extra("window_days", window_days)
            sentry_sdk.capture_exception(exc)
        rows = []

    cutoff = datetime.now(UTC) - timedelta(days=window_days)
    try:
        for row in rows:
            created_at = _parse_iso_datetime(row.get("created_at"))
            if created_at is None or created_at < cutoff:
                continue

            email_type = _resolve_email_type(row)
            if email_type is None:
                continue

            counter = counters[email_type]
            counter.sent += 1
            if _is_delivered(row):
                counter.delivered += 1
            if _is_opened(row):
                counter.opened += 1
    except Exception as exc:
        with sentry_sdk.new_scope() as scope:
            scope.set_tag("error_code", "EMAIL_METRICS_AGGREGATION_FAILED")
            scope.set_extra("window_days", window_days)
            sentry_sdk.capture_exception(exc)

    result_c = counters["result"]
    magic_c = counters["magic_link"]
    f1_c = counters["followup_day1"]
    f3_c = counters["followup_day3"]
    f7_c = counters["followup_day7"]

    followup_sent = f1_c.sent + f3_c.sent + f7_c.sent
    followup_delivered = f1_c.delivered + f3_c.delivered + f7_c.delivered
    followup_opened = f1_c.opened + f3_c.opened + f7_c.opened

    # overall_delivery_rate and its alert cover result + follow-up emails only.
    # Magic link is transactional and has a different expected delivery profile.
    alert_sent = result_c.sent + followup_sent
    alert_delivered = result_c.delivered + followup_delivered
    overall_delivery_rate = _delivery_rate(sent=alert_sent, delivered=alert_delivered)

    _emit_delivery_health_alert_if_needed(
        rate=overall_delivery_rate,
        window_days=window_days,
        total_sent=alert_sent,
    )

    return OperatorEmailStatsResponse(
        window_days=window_days,
        result_emails_sent=result_c.sent,
        result_delivery_rate=_delivery_rate(
            sent=result_c.sent, delivered=result_c.delivered
        ),
        result_open_rate=_open_rate(
            delivered=result_c.delivered, opened=result_c.opened
        ),
        magic_link_sent=magic_c.sent,
        magic_link_delivery_rate=_delivery_rate(
            sent=magic_c.sent, delivered=magic_c.delivered
        ),
        followup_day1_sent=f1_c.sent,
        followup_day3_sent=f3_c.sent,
        followup_day7_sent=f7_c.sent,
        followup_delivery_rate=_delivery_rate(
            sent=followup_sent, delivered=followup_delivered
        ),
        followup_open_rate=_open_rate(
            delivered=followup_delivered, opened=followup_opened
        ),
        overall_delivery_rate=overall_delivery_rate,
    )
