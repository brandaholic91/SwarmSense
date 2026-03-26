from __future__ import annotations

from typing import Any
from unittest.mock import patch

import pytest

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
    monkeypatch.setenv("SWARMSENSE_BACKEND_ORIGIN", "https://api.swarmsense.ai")
    monkeypatch.setenv("SWARMSENSE_RESEND_API_KEY", "re_test")
    monkeypatch.setenv("SWARMSENSE_OPENROUTER_API_KEY", "or_test")
    monkeypatch.setenv("SWARMSENSE_EMAIL_FROM", "SwarmSense <noreply@swarmsense.ai>")
    monkeypatch.setenv("SWARMSENSE_EMAIL_REPLY_TO", "support@swarmsense.ai")
    get_settings.cache_clear()


RENDERED_HTML = (
    "<html><body>"
    "<p>Itt van a SwarmSense eredmenyed</p>"
    "<p>12/15 persona valaszolt</p>"
    "<p>Aggregalt tamogatasi arany: Tamogatja: 6 | Elutasitja: 3 | Felteteles: 3</p>"
    "<p>Kutatasi tema: Erdemes-e arat emelni?</p>"
    "<p>Celkozonseg: KKV marketing vezetok</p>"
    "</body></html>"
)


@pytest.fixture
def mock_render_email(monkeypatch) -> None:
    import html

    def _mock_render(*, props: dict[str, Any], frontend_origin: str) -> str:
        topic = html.escape(str(props.get("topic", "")))
        return (
            "<html><body>"
            f"<p>Itt van a SwarmSense eredmenyed</p>"
            f"<p>{topic}</p>"
            f"<p>12/15 persona valaszolt</p>"
            "<p>Aggregalt tamogatasi arany: Tamogatja: 6 | Elutasitja: 3 | Felteteles: 3</p>"
            "<p>Kutatasi tema: Erdemes-e arat emelni?</p>"
            "<p>Celkozonseg: KKV marketing vezetok</p>"
            "</body></html>"
        )

    monkeypatch.setattr(
        "app.services.email_service._render_result_email_via_frontend_api",
        _mock_render,
    )


def test_send_run_result_email_uses_required_subject_and_reply_to(
    monkeypatch, mock_render_email
) -> None:
    _seed_env(monkeypatch)
    from app.services.email_service import send_run_result_email

    sent: list[dict[str, Any]] = []

    with patch("resend.Emails.send", side_effect=lambda payload: sent.append(payload)):
        send_run_result_email(
            recipient_email="user@example.com",
            result_payload=TEST_RESULT_PAYLOAD,
        )

    assert len(sent) == 1
    assert sent[0]["subject"] == "A SwarmSense elemzésed elkészült"
    assert sent[0]["reply_to"] == "support@swarmsense.ai"
    assert sent[0]["tags"] == [{"name": "email_type", "value": "result"}]


def test_send_run_result_email_falls_back_reply_to_when_empty(
    monkeypatch, mock_render_email
) -> None:
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


def test_send_run_result_email_renders_partial_count_text(
    monkeypatch, mock_render_email
) -> None:
    _seed_env(monkeypatch)
    from app.services.email_service import send_run_result_email

    sent: list[dict[str, Any]] = []

    with patch("resend.Emails.send", side_effect=lambda payload: sent.append(payload)):
        send_run_result_email(
            recipient_email="user@example.com",
            result_payload=TEST_RESULT_PAYLOAD,
        )

    assert "12/15 persona valaszolt" in sent[0]["html"]


def test_send_run_result_email_html_escapes_user_content(
    monkeypatch, mock_render_email
) -> None:
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


def test_send_magic_link_email_uses_frontend_rendered_template(monkeypatch) -> None:
    _seed_env(monkeypatch)
    from app.services.email_service import send_magic_link_email

    sent: list[dict[str, Any]] = []

    monkeypatch.setattr(
        "app.services.email_service._render_magic_link_email_via_frontend_api",
        lambda *, props, frontend_origin: (
            f"<html><body>magic:{props['verify_url']}:{frontend_origin}</body></html>"
        ),
    )

    with patch("resend.Emails.send", side_effect=lambda payload: sent.append(payload)):
        send_magic_link_email(
            recipient_email="user@example.com",
            verify_url="https://swarmsense.vercel.app/verify?token=test-token",
        )

    assert len(sent) == 1
    assert sent[0]["subject"] == "SwarmSense – Bejelentkezési link"
    assert sent[0]["reply_to"] == "support@swarmsense.ai"
    assert sent[0]["tags"] == [{"name": "email_type", "value": "magic_link"}]
    assert (
        "magic:https://swarmsense.vercel.app/verify?token=test-token" in sent[0]["html"]
    )


def test_send_followup_email_uses_day_template_and_unsubscribe_link(
    monkeypatch,
) -> None:
    _seed_env(monkeypatch)
    from app.services.email_service import send_followup_email

    sent: list[dict[str, Any]] = []

    monkeypatch.setattr(
        "app.services.email_service._render_followup_email_via_frontend_api",
        lambda *, day, props, frontend_origin: (
            f"<html><body>{day}:{props['unsubscribe_url']}:{frontend_origin}</body></html>"
        ),
    )

    with patch("resend.Emails.send", side_effect=lambda payload: sent.append(payload)):
        send_followup_email(
            recipient_email="user@example.com",
            day="day3",
            user_id="11111111-1111-4111-8111-111111111111",
        )

    assert len(sent) == 1
    assert sent[0]["subject"] == "Új nézőpontok a SwarmSense eredményedhez"
    assert "day3:" in sent[0]["html"]
    assert (
        "https://api.swarmsense.ai/api/v1/unsubscribe?user_id=11111111-1111-4111-8111-111111111111"
        in sent[0]["html"]
    )
    assert "List-Unsubscribe" in sent[0]["headers"]
    assert "List-Unsubscribe-Post" in sent[0]["headers"]
    assert sent[0]["headers"]["List-Unsubscribe-Post"] == "List-Unsubscribe=One-Click"
    assert sent[0]["tags"] == [{"name": "email_type", "value": "followup_day3"}]


def test_send_followup_day1_email_sets_correct_tag(monkeypatch) -> None:
    _seed_env(monkeypatch)
    from app.services.email_service import send_followup_email

    sent: list[dict[str, Any]] = []

    monkeypatch.setattr(
        "app.services.email_service._render_followup_email_via_frontend_api",
        lambda *, day, props, frontend_origin: "<html><body>day1</body></html>",
    )

    with patch("resend.Emails.send", side_effect=lambda payload: sent.append(payload)):
        send_followup_email(
            recipient_email="user@example.com",
            day="day1",
            user_id="11111111-1111-4111-8111-111111111111",
        )

    assert len(sent) == 1
    assert sent[0]["tags"] == [{"name": "email_type", "value": "followup_day1"}]


def test_send_followup_day7_email_sets_correct_tag(monkeypatch) -> None:
    _seed_env(monkeypatch)
    from app.services.email_service import send_followup_email

    sent: list[dict[str, Any]] = []

    monkeypatch.setattr(
        "app.services.email_service._render_followup_email_via_frontend_api",
        lambda *, day, props, frontend_origin: "<html><body>day7</body></html>",
    )

    with patch("resend.Emails.send", side_effect=lambda payload: sent.append(payload)):
        send_followup_email(
            recipient_email="user@example.com",
            day="day7",
            user_id="11111111-1111-4111-8111-111111111111",
        )

    assert len(sent) == 1
    assert sent[0]["tags"] == [{"name": "email_type", "value": "followup_day7"}]


class _FakeResponse:
    def __init__(self, data: list[dict[str, Any]]):
        self.data = data


class _FakeUsersQuery:
    def __init__(self, rows: list[dict[str, Any]]):
        self._rows = rows
        self._user_id: str | None = None

    def select(self, _fields: str):
        return self

    def eq(self, field: str, value: str):
        if field == "id":
            self._user_id = value
        return self

    def limit(self, _value: int):
        return self

    def execute(self):
        filtered = [
            row
            for row in self._rows
            if self._user_id is None or str(row.get("id")) == self._user_id
        ]
        return _FakeResponse(filtered[:1])


class _FakeSupabase:
    def __init__(self, rows: list[dict[str, Any]]):
        self._rows = rows

    def table(self, table_name: str):
        assert table_name == "users"
        return _FakeUsersQuery(self._rows)


def test_send_run_result_email_skips_unsubscribed_user(monkeypatch, mock_render_email) -> None:
    _seed_env(monkeypatch)
    from app.services.email_service import send_run_result_email

    monkeypatch.setattr(
        "app.services.consent_service.get_supabase_client",
        lambda: _FakeSupabase(
            [{"id": "u-1", "email": "user@example.com", "unsubscribed_at": "2026-03-26T10:00:00Z"}]
        ),
    )

    sent: list[dict[str, Any]] = []
    with patch("resend.Emails.send", side_effect=lambda payload: sent.append(payload)):
        send_run_result_email(
            recipient_email="user@example.com",
            result_payload=TEST_RESULT_PAYLOAD,
            user_id="u-1",
        )

    assert sent == []
