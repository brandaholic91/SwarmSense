from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

from app.services import email_metrics


def _email_row(
    *,
    email_type: str,
    created_at: datetime,
    last_event: str,
    opens: int = 0,
) -> dict[str, Any]:
    return {
        "created_at": created_at.isoformat(),
        "last_event": last_event,
        "opens": opens,
        "tags": [{"name": "email_type", "value": email_type}],
    }


def test_get_email_stats_summary_aggregates_delivery_and_open_rates(
    monkeypatch,
) -> None:
    now = datetime.now(UTC)
    rows = [
        _email_row(
            email_type="result",
            created_at=now - timedelta(days=1),
            last_event="delivered",
            opens=1,
        ),
        _email_row(
            email_type="result",
            created_at=now - timedelta(days=1),
            last_event="bounced",
        ),
        _email_row(
            email_type="magic_link",
            created_at=now - timedelta(days=2),
            last_event="delivered",
        ),
        _email_row(
            email_type="followup_day1",
            created_at=now - timedelta(days=2),
            last_event="opened",
            opens=1,
        ),
        _email_row(
            email_type="followup_day3",
            created_at=now - timedelta(days=4),
            last_event="delivered",
            opens=0,
        ),
        _email_row(
            email_type="followup_day7",
            created_at=now - timedelta(days=6),
            last_event="bounced",
            opens=0,
        ),
    ]

    monkeypatch.setattr(email_metrics, "_load_resend_emails", lambda: rows)
    monkeypatch.setattr(
        email_metrics,
        "_emit_delivery_health_alert_if_needed",
        lambda **kwargs: None,
    )

    stats = email_metrics.get_email_stats_summary(window_days=7)

    assert stats.window_days == 7
    assert stats.result_emails_sent == 2
    assert stats.result_delivery_rate == 0.5
    assert stats.result_open_rate == 0.5
    assert stats.magic_link_sent == 1
    assert stats.magic_link_delivery_rate == 1.0
    assert stats.followup_day1_sent == 1
    assert stats.followup_day3_sent == 1
    assert stats.followup_day7_sent == 1
    assert abs(stats.followup_delivery_rate - (2 / 3)) < 0.00001
    assert abs(stats.followup_open_rate - (1 / 3)) < 0.00001
    assert abs(stats.overall_delivery_rate - (4 / 6)) < 0.00001


def test_get_email_stats_summary_returns_zeroed_payload_for_provider_failure(
    monkeypatch,
) -> None:
    captured: list[Exception] = []

    def _raise() -> list[dict[str, Any]]:
        raise RuntimeError("resend unavailable")

    monkeypatch.setattr(email_metrics, "_load_resend_emails", _raise)
    monkeypatch.setattr(
        email_metrics.sentry_sdk,
        "capture_exception",
        lambda exc: captured.append(exc),
    )

    stats = email_metrics.get_email_stats_summary(window_days=7)

    assert stats.result_emails_sent == 0
    assert stats.result_delivery_rate == 0.0
    assert stats.followup_day1_sent == 0
    assert stats.followup_day3_sent == 0
    assert stats.followup_day7_sent == 0
    assert stats.followup_open_rate == 0.0
    assert stats.overall_delivery_rate == 0.0
    assert len(captured) == 1


def test_delivery_alert_threshold_triggers_and_dedupes(monkeypatch) -> None:
    email_metrics.reset_email_delivery_alert_state_for_tests()
    alerts: list[str] = []

    monkeypatch.setattr(
        email_metrics.sentry_sdk,
        "capture_message",
        lambda message, level="warning": alerts.append(str(message)),
    )

    email_metrics._emit_delivery_health_alert_if_needed(
        rate=0.94,
        window_days=7,
        total_sent=100,
    )
    email_metrics._emit_delivery_health_alert_if_needed(
        rate=0.94,
        window_days=7,
        total_sent=100,
    )

    assert len(alerts) == 1

    email_metrics._emit_delivery_health_alert_if_needed(
        rate=0.97,
        window_days=7,
        total_sent=100,
    )
    email_metrics._emit_delivery_health_alert_if_needed(
        rate=0.94,
        window_days=7,
        total_sent=100,
    )

    assert len(alerts) == 2
