from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from threading import Lock
from typing import Any

import resend
import sentry_sdk

from app.core.config import get_settings
from app.models.operator import OperatorEmailStatsResponse

DELIVERY_ALERT_THRESHOLD = 0.95
DEFAULT_WINDOW_DAYS = 7
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
_alert_state_lock = Lock()
_last_alert_bucket: float | None = None


@dataclass
class _EmailTypeCounter:
    sent: int = 0
    delivered: int = 0
    opened: int = 0


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
    if isinstance(value, bool):
        return 0
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
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

    subject_raw = email_row.get("subject")
    subject = subject_raw.lower() if isinstance(subject_raw, str) else ""
    if "bejelentkez" in subject:
        return "magic_link"
    if "elemz" in subject and "elkesz" in subject:
        return "result"
    if "24" in subject:
        return "followup_day1"
    if "het" in subject and "egy" not in subject:
        return "followup_day3"
    if "egy h" in subject:
        return "followup_day7"
    return None


def _is_delivered(email_row: dict[str, Any]) -> bool:
    last_event = email_row.get("last_event")
    if isinstance(last_event, str) and last_event.strip().lower() in _SUCCESS_EVENTS:
        return True

    delivered_at = email_row.get("delivered_at")
    if isinstance(delivered_at, str) and delivered_at.strip():
        return True

    event_counts = email_row.get("event_counts")
    if isinstance(event_counts, dict):
        delivered_count = _safe_int(event_counts.get("delivered"))
        if delivered_count > 0:
            return True
    return False


def _is_opened(email_row: dict[str, Any]) -> bool:
    last_event = email_row.get("last_event")
    if isinstance(last_event, str) and last_event.strip().lower() in _OPEN_EVENTS:
        return True

    opens_value = email_row.get("opens")
    if _safe_int(opens_value) > 0:
        return True

    open_count = email_row.get("open_count")
    return _safe_int(open_count) > 0


def _delivery_rate(*, sent: int, delivered: int) -> float:
    if sent <= 0:
        return 0.0
    return delivered / sent


def _open_rate(*, sent: int, opened: int) -> float:
    if sent <= 0:
        return 0.0
    return opened / sent


def _load_resend_emails() -> list[dict[str, Any]]:
    settings = get_settings()
    resend.api_key = settings.resend_api_key
    try:
        result = resend.Emails.list(params={"limit": 100})
    except TypeError:
        result = resend.Emails.list()

    if isinstance(result, dict):
        data = result.get("data")
        if isinstance(data, list):
            return [item for item in data if isinstance(item, dict)]
    if isinstance(result, list):
        return [item for item in result if isinstance(item, dict)]
    return []


def _emit_delivery_health_alert_if_needed(
    *,
    rate: float,
    window_days: int,
    total_sent: int,
) -> None:
    global _last_alert_bucket

    if rate >= DELIVERY_ALERT_THRESHOLD:
        with _alert_state_lock:
            _last_alert_bucket = None
        return

    current_bucket = round(rate, 4)
    with _alert_state_lock:
        if _last_alert_bucket == current_bucket:
            return
        _last_alert_bucket = current_bucket

    with sentry_sdk.push_scope() as scope:
        scope.set_tag("alert_type", "email_delivery_rate_degraded")
        scope.set_tag("threshold", "95_percent")
        scope.set_extra("window_days", window_days)
        scope.set_extra("overall_delivery_rate", rate)
        scope.set_extra("total_sent", total_sent)
        sentry_sdk.capture_message(
            (
                "7-day email delivery success rate dropped below 95%: "
                f"rate={rate:.4f}, sent={total_sent}"
            ),
            level="warning",
        )


def reset_email_delivery_alert_state_for_tests() -> None:
    global _last_alert_bucket
    with _alert_state_lock:
        _last_alert_bucket = None


def get_email_stats_summary(
    *, window_days: int = DEFAULT_WINDOW_DAYS
) -> OperatorEmailStatsResponse:
    counters = {
        "result": _EmailTypeCounter(),
        "magic_link": _EmailTypeCounter(),
        "followup_day1": _EmailTypeCounter(),
        "followup_day3": _EmailTypeCounter(),
        "followup_day7": _EmailTypeCounter(),
    }

    try:
        rows = _load_resend_emails()
    except Exception as exc:
        with sentry_sdk.push_scope() as scope:
            scope.set_tag("error_code", "EMAIL_METRICS_FETCH_FAILED")
            scope.set_extra("window_days", window_days)
            sentry_sdk.capture_exception(exc)
        rows = []

    cutoff = datetime.now(UTC) - timedelta(days=window_days)
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

    result_sent = counters["result"].sent
    result_delivered = counters["result"].delivered
    result_opened = counters["result"].opened

    magic_link_sent = counters["magic_link"].sent
    magic_link_delivered = counters["magic_link"].delivered

    followup_sent = (
        counters["followup_day1"].sent
        + counters["followup_day3"].sent
        + counters["followup_day7"].sent
    )
    followup_delivered = (
        counters["followup_day1"].delivered
        + counters["followup_day3"].delivered
        + counters["followup_day7"].delivered
    )
    followup_opened = (
        counters["followup_day1"].opened
        + counters["followup_day3"].opened
        + counters["followup_day7"].opened
    )

    overall_sent = result_sent + magic_link_sent + followup_sent
    overall_delivered = result_delivered + magic_link_delivered + followup_delivered
    overall_delivery_rate = _delivery_rate(
        sent=overall_sent, delivered=overall_delivered
    )

    _emit_delivery_health_alert_if_needed(
        rate=overall_delivery_rate,
        window_days=window_days,
        total_sent=overall_sent,
    )

    return OperatorEmailStatsResponse(
        window_days=window_days,
        result_emails_sent=result_sent,
        result_delivery_rate=_delivery_rate(
            sent=result_sent, delivered=result_delivered
        ),
        result_open_rate=_open_rate(sent=result_sent, opened=result_opened),
        magic_link_sent=magic_link_sent,
        magic_link_delivery_rate=_delivery_rate(
            sent=magic_link_sent,
            delivered=magic_link_delivered,
        ),
        followup_day1_sent=counters["followup_day1"].sent,
        followup_day3_sent=counters["followup_day3"].sent,
        followup_day7_sent=counters["followup_day7"].sent,
        followup_delivery_rate=_delivery_rate(
            sent=followup_sent,
            delivered=followup_delivered,
        ),
        followup_open_rate=_open_rate(sent=followup_sent, opened=followup_opened),
        overall_delivery_rate=overall_delivery_rate,
    )
