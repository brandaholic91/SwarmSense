from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any
from unittest.mock import MagicMock, patch

from app.services import email_metrics


def _email_row(
    *,
    email_type: str,
    created_at: datetime,
    last_event: str,
    opens: int = 0,
) -> dict[str, Any]:
    return {
        "id": f"test-{email_type}",
        "created_at": created_at.isoformat(),
        "last_event": last_event,
        "opens": opens,
        "tags": [{"name": "email_type", "value": email_type}],
    }


# ---------------------------------------------------------------------------
# Aggregation correctness
# ---------------------------------------------------------------------------


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
    # result: 1 delivered out of 2 sent
    assert stats.result_delivery_rate == 0.5
    # result open rate = opens / delivered = 1 / 1 = 1.0 (IG-1 fix)
    assert stats.result_open_rate == 1.0
    assert stats.magic_link_sent == 1
    assert stats.magic_link_delivery_rate == 1.0
    assert stats.followup_day1_sent == 1
    assert stats.followup_day3_sent == 1
    assert stats.followup_day7_sent == 1
    # followup: day1 delivered (opened counts), day3 delivered, day7 bounced → 2/3 delivered
    assert abs(stats.followup_delivery_rate - (2 / 3)) < 0.00001
    # followup open rate = opens / delivered = 1 / 2 (day1 opened, day3 not opened)
    assert abs(stats.followup_open_rate - (1 / 2)) < 0.00001
    # overall = result + followup only (magic_link excluded per IG-2)
    # result: 1 delivered; followup: 2 delivered; total: 3/5 = 0.6
    assert abs(stats.overall_delivery_rate - (3 / 5)) < 0.00001


def test_open_rate_uses_delivered_denominator_not_sent(monkeypatch) -> None:
    """open_rate = opens/delivered, not opens/sent."""
    now = datetime.now(UTC)
    rows = [
        # 3 result emails sent; 2 delivered; 1 opened
        _email_row(
            email_type="result",
            created_at=now - timedelta(days=1),
            last_event="delivered",
            opens=1,
        ),
        _email_row(
            email_type="result",
            created_at=now - timedelta(days=1),
            last_event="delivered",
            opens=0,
        ),
        _email_row(
            email_type="result",
            created_at=now - timedelta(days=1),
            last_event="bounced",
        ),
    ]

    monkeypatch.setattr(email_metrics, "_load_resend_emails", lambda: rows)
    monkeypatch.setattr(
        email_metrics,
        "_emit_delivery_health_alert_if_needed",
        lambda **kwargs: None,
    )

    stats = email_metrics.get_email_stats_summary(window_days=7)

    assert stats.result_emails_sent == 3
    assert stats.result_delivery_rate == pytest_approx(2 / 3)
    # opens/delivered = 1/2, NOT opens/sent = 1/3
    assert stats.result_open_rate == pytest_approx(1 / 2)


def pytest_approx(value: float) -> Any:  # noqa: N802 — helper
    """Simple wrapper for float comparison tolerance."""
    class _Approx:
        def __eq__(self, other: object) -> bool:
            if not isinstance(other, float):
                return NotImplemented
            return abs(other - value) < 1e-9
        def __repr__(self) -> str:
            return f"≈{value}"
    return _Approx()


def test_overall_delivery_rate_excludes_magic_link(monkeypatch) -> None:
    """magic_link rows must not affect overall_delivery_rate or the alert threshold."""
    now = datetime.now(UTC)
    rows = [
        _email_row(
            email_type="result",
            created_at=now - timedelta(days=1),
            last_event="delivered",
        ),
        # magic_link bounces — must NOT pull overall_delivery_rate below threshold
        _email_row(
            email_type="magic_link",
            created_at=now - timedelta(days=1),
            last_event="bounced",
        ),
        _email_row(
            email_type="magic_link",
            created_at=now - timedelta(days=1),
            last_event="bounced",
        ),
        _email_row(
            email_type="magic_link",
            created_at=now - timedelta(days=1),
            last_event="bounced",
        ),
    ]

    alert_calls: list[dict[str, Any]] = []
    monkeypatch.setattr(email_metrics, "_load_resend_emails", lambda: rows)
    monkeypatch.setattr(
        email_metrics,
        "_emit_delivery_health_alert_if_needed",
        lambda **kwargs: alert_calls.append(kwargs),
    )

    stats = email_metrics.get_email_stats_summary(window_days=7)

    # result: 1/1 = 100% delivery; magic_link excluded from overall
    assert stats.overall_delivery_rate == 1.0
    assert alert_calls[0]["total_sent"] == 1  # only result counted
    assert alert_calls[0]["rate"] == 1.0


# ---------------------------------------------------------------------------
# Provider failure resilience
# ---------------------------------------------------------------------------


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
    assert stats.result_open_rate == 0.0
    assert stats.followup_day1_sent == 0
    assert stats.followup_day3_sent == 0
    assert stats.followup_day7_sent == 0
    assert stats.followup_open_rate == 0.0
    assert stats.overall_delivery_rate == 0.0
    assert len(captured) == 1


def test_get_email_stats_summary_handles_partial_malformed_rows(
    monkeypatch,
) -> None:
    """Rows with missing/malformed fields are skipped; valid rows still counted."""
    now = datetime.now(UTC)
    rows: list[dict[str, Any]] = [
        # no created_at → skip
        {"id": "r1", "tags": [{"name": "email_type", "value": "result"}], "last_event": "delivered"},
        # created_at is null → skip
        {"id": "r2", "created_at": None, "tags": [{"name": "email_type", "value": "result"}], "last_event": "delivered"},
        # empty tags and no subject → unresolved type → skip
        {"id": "r3", "created_at": (now - timedelta(days=1)).isoformat(), "tags": [], "last_event": "delivered"},
        # missing last_event → sent=1, delivered=0
        {"id": "r4", "created_at": (now - timedelta(days=1)).isoformat(), "tags": [{"name": "email_type", "value": "result"}]},
        # valid delivered row
        _email_row(email_type="result", created_at=now - timedelta(days=1), last_event="delivered"),
    ]

    monkeypatch.setattr(email_metrics, "_load_resend_emails", lambda: rows)
    monkeypatch.setattr(
        email_metrics,
        "_emit_delivery_health_alert_if_needed",
        lambda **kwargs: None,
    )

    stats = email_metrics.get_email_stats_summary(window_days=7)

    # r4 (sent, not delivered) + valid row (sent + delivered)
    assert stats.result_emails_sent == 2
    assert stats.result_delivery_rate == 0.5


# ---------------------------------------------------------------------------
# Alert threshold and dedup
# ---------------------------------------------------------------------------


def test_delivery_alert_does_not_fire_when_total_sent_is_zero(monkeypatch) -> None:
    """Empty sending window must not trigger a false degradation alert."""
    email_metrics.reset_email_delivery_alert_state_for_tests()
    alerts: list[str] = []

    monkeypatch.setattr(
        email_metrics.sentry_sdk,
        "capture_message",
        lambda message, level="warning": alerts.append(str(message)),
    )

    email_metrics._emit_delivery_health_alert_if_needed(
        rate=0.0,
        window_days=7,
        total_sent=0,
    )

    assert len(alerts) == 0


def test_delivery_alert_does_not_fire_at_or_above_threshold_from_cold_state(
    monkeypatch,
) -> None:
    """rate >= 0.95 must never trigger an alert, even from a fresh state."""
    email_metrics.reset_email_delivery_alert_state_for_tests()
    alerts: list[str] = []

    monkeypatch.setattr(
        email_metrics.sentry_sdk,
        "capture_message",
        lambda message, level="warning": alerts.append(str(message)),
    )

    for rate in (0.95, 0.97, 1.0):
        email_metrics._emit_delivery_health_alert_if_needed(
            rate=rate,
            window_days=7,
            total_sent=50,
        )

    assert len(alerts) == 0


def test_delivery_alert_threshold_triggers_and_dedupes(monkeypatch) -> None:
    email_metrics.reset_email_delivery_alert_state_for_tests()
    alerts: list[str] = []

    monkeypatch.setattr(
        email_metrics.sentry_sdk,
        "capture_message",
        lambda message, level="warning": alerts.append(str(message)),
    )

    # First call — fires
    email_metrics._emit_delivery_health_alert_if_needed(rate=0.94, window_days=7, total_sent=100)
    # Same bucket — deduped
    email_metrics._emit_delivery_health_alert_if_needed(rate=0.94, window_days=7, total_sent=100)

    assert len(alerts) == 1

    # Recovery resets bucket
    email_metrics._emit_delivery_health_alert_if_needed(rate=0.97, window_days=7, total_sent=100)
    # Re-degradation after recovery — fires again
    email_metrics._emit_delivery_health_alert_if_needed(rate=0.94, window_days=7, total_sent=100)

    assert len(alerts) == 2


def test_delivery_alert_message_uses_dynamic_window_days(monkeypatch) -> None:
    email_metrics.reset_email_delivery_alert_state_for_tests()
    captured: list[str] = []

    monkeypatch.setattr(
        email_metrics.sentry_sdk,
        "capture_message",
        lambda message, level="warning": captured.append(str(message)),
    )

    email_metrics._emit_delivery_health_alert_if_needed(rate=0.90, window_days=14, total_sent=200)

    assert len(captured) == 1
    assert "14-day" in captured[0]
    assert "7-day" not in captured[0]


def test_delivery_alert_bucket_restored_on_sentry_failure(monkeypatch) -> None:
    """If capture_message raises, the bucket is restored so the next call can retry."""
    email_metrics.reset_email_delivery_alert_state_for_tests()
    call_count = 0

    def _fail(message: str, level: str = "warning") -> None:
        nonlocal call_count
        call_count += 1
        raise RuntimeError("sentry down")

    monkeypatch.setattr(email_metrics.sentry_sdk, "capture_message", _fail)

    email_metrics._emit_delivery_health_alert_if_needed(rate=0.90, window_days=7, total_sent=100)
    assert call_count == 1  # attempted

    # Bucket was restored — a second call with same rate must retry
    email_metrics._emit_delivery_health_alert_if_needed(rate=0.90, window_days=7, total_sent=100)
    assert call_count == 2
