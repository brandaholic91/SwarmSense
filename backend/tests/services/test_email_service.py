from __future__ import annotations

import html
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from app.core.config import get_settings


TEST_RESULT_PAYLOAD: dict[str, Any] = {
    "run_id": "run-1",
    "status": "partial",
    "completed_persona_count": 12,
    "total_persona_count": 15,
    "persona_count_label": "12/15 persona",
    "stance_counts": {"support": 6, "reject": 3, "conditional": 3},
    "top_arguments": ["Erv-1", "Erv-2"],
    "personas": [],
}


def _seed_env(monkeypatch) -> None:
    monkeypatch.setenv("SWARMSENSE_SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setenv("SWARMSENSE_SUPABASE_SERVICE_KEY", "service-key")
    monkeypatch.setenv("SWARMSENSE_KIMI_API_KEY", "kimi-key")
    monkeypatch.setenv("SWARMSENSE_OPERATOR_API_KEY", "operator-key")
    monkeypatch.setenv("SWARMSENSE_INTERNAL_SECRET", "test-secret")
    monkeypatch.setenv("SWARMSENSE_ENVIRONMENT", "development")
    monkeypatch.setenv("SWARMSENSE_FRONTEND_ORIGIN", "https://swarmsense.vercel.app")
    monkeypatch.setenv("SWARMSENSE_RESEND_API_KEY", "re_test")
    monkeypatch.setenv("SWARMSENSE_OPENROUTER_API_KEY", "or_test")
    get_settings.cache_clear()


def test_send_run_result_email_persona_count_label_in_subject(monkeypatch) -> None:
    _seed_env(monkeypatch)
    from app.services.email_service import send_run_result_email

    sent: list[dict[str, Any]] = []

    with patch("resend.Emails.send", side_effect=lambda payload: sent.append(payload)):
        send_run_result_email(
            recipient_email="user@example.com",
            result_payload=TEST_RESULT_PAYLOAD,
        )

    assert len(sent) == 1
    assert "12/15 persona" in sent[0]["subject"]


def test_send_run_result_email_persona_count_label_in_html_header(monkeypatch) -> None:
    _seed_env(monkeypatch)
    from app.services.email_service import send_run_result_email

    sent: list[dict[str, Any]] = []

    with patch("resend.Emails.send", side_effect=lambda payload: sent.append(payload)):
        send_run_result_email(
            recipient_email="user@example.com",
            result_payload=TEST_RESULT_PAYLOAD,
        )

    assert "12/15 persona" in sent[0]["html"]


def test_send_run_result_email_html_escapes_user_content(monkeypatch) -> None:
    _seed_env(monkeypatch)
    from app.services.email_service import send_run_result_email

    malicious_payload = dict(TEST_RESULT_PAYLOAD)
    malicious_payload["top_arguments"] = ["</pre><script>alert(1)</script>"]

    sent: list[dict[str, Any]] = []

    with patch("resend.Emails.send", side_effect=lambda payload: sent.append(payload)):
        send_run_result_email(
            recipient_email="user@example.com",
            result_payload=malicious_payload,
        )

    body = sent[0]["html"]
    assert "<script>" not in body
    assert html.escape("</pre><script>alert(1)</script>") in body


def test_send_run_result_email_sends_to_correct_recipient(monkeypatch) -> None:
    _seed_env(monkeypatch)
    from app.services.email_service import send_run_result_email

    sent: list[dict[str, Any]] = []

    with patch("resend.Emails.send", side_effect=lambda payload: sent.append(payload)):
        send_run_result_email(
            recipient_email="target@example.com",
            result_payload=TEST_RESULT_PAYLOAD,
        )

    assert sent[0]["to"] == ["target@example.com"]
