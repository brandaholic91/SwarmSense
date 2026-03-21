from __future__ import annotations

from typing import Any
from unittest.mock import patch

from app.core.config import get_settings


TEST_RESULT_PAYLOAD: dict[str, Any] = {
    "run_id": "run-1",
    "status": "partial",
    "topic": "Erdemes-e arat emelni?",
    "audience": "KKV marketing vezetok",
    "completed_persona_count": 12,
    "total_persona_count": 15,
    "persona_count_label": "12/15 persona",
    "persona_count_header_display": "12/15 persona valaszolt",
    "aggregate_score_display": "Tamogatja: 6 | Elutasitja: 3 | Felteteles: 3",
    "consensus_flag_display": "",
    "personas": [
        {
            "name": "Kovacs Peter",
            "role": "CFO",
            "stance": "reject",
            "primary_argument": "Tul nagy lemorzsolodas varhato.",
            "change_condition": "Ha bizonyitottan no az ertek.",
        }
    ],
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
    monkeypatch.setenv("SWARMSENSE_EMAIL_FROM", "SwarmSense <noreply@swarmsense.ai>")
    monkeypatch.setenv("SWARMSENSE_EMAIL_REPLY_TO", "support@swarmsense.ai")
    get_settings.cache_clear()


def test_send_run_result_email_uses_required_subject_and_reply_to(monkeypatch) -> None:
    _seed_env(monkeypatch)
    from app.services.email_service import send_run_result_email

    sent: list[dict[str, Any]] = []

    with patch("resend.Emails.send", side_effect=lambda payload: sent.append(payload)):
        send_run_result_email(
            recipient_email="user@example.com",
            result_payload=TEST_RESULT_PAYLOAD,
        )

    assert len(sent) == 1
    assert sent[0]["subject"] == "A SwarmSense elemzesed elkeszult"
    assert sent[0]["reply_to"] == "support@swarmsense.ai"


def test_send_run_result_email_falls_back_reply_to_when_empty(monkeypatch) -> None:
    _seed_env(monkeypatch)
    monkeypatch.setenv("SWARMSENSE_EMAIL_REPLY_TO", "   ")
    get_settings.cache_clear()
    from app.services.email_service import send_run_result_email

    sent: list[dict[str, Any]] = []

    with patch("resend.Emails.send", side_effect=lambda payload: sent.append(payload)):
        send_run_result_email(
            recipient_email="user@example.com",
            result_payload=TEST_RESULT_PAYLOAD,
        )

    assert sent[0]["reply_to"] == "SwarmSense <noreply@swarmsense.ai>"


def test_send_run_result_email_renders_partial_count_text(monkeypatch) -> None:
    _seed_env(monkeypatch)
    from app.services.email_service import send_run_result_email

    sent: list[dict[str, Any]] = []

    with patch("resend.Emails.send", side_effect=lambda payload: sent.append(payload)):
        send_run_result_email(
            recipient_email="user@example.com",
            result_payload=TEST_RESULT_PAYLOAD,
        )

    assert "12/15 persona valaszolt" in sent[0]["html"]


def test_send_run_result_email_html_escapes_user_content(monkeypatch) -> None:
    _seed_env(monkeypatch)
    from app.services.email_service import send_run_result_email

    malicious_payload = dict(TEST_RESULT_PAYLOAD)
    malicious_payload["topic"] = "</p><script>alert(1)</script>"

    sent: list[dict[str, Any]] = []

    with patch("resend.Emails.send", side_effect=lambda payload: sent.append(payload)):
        send_run_result_email(
            recipient_email="user@example.com",
            result_payload=malicious_payload,
        )

    body = sent[0]["html"]
    assert "<script>" not in body
    assert "&lt;/p&gt;&lt;script&gt;alert(1)&lt;/script&gt;" in body
