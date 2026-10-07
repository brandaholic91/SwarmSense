from __future__ import annotations

import base64

import pytest

from app.services import email_service

RUN_ID = "0b6f1c1e-8f7a-4c1e-9d3e-2a5b7c9d1e3f"
ADDRESS = "reader@example.test"


def test_build_email_escapes_topic():
    subject, body = email_service.build_email(topic="<b>x</b> & y", run_id=RUN_ID)

    assert "&lt;b&gt;x&lt;/b&gt; &amp; y" in body
    assert "<b>x</b>" not in body
    assert f"http://localhost:3000/eredmeny/{RUN_ID}" in body
    assert subject


def test_send_posts_expected_payload(monkeypatch):
    sent: list[dict] = []
    monkeypatch.setattr(email_service, "_post_resend", sent.append)
    pdf = b"%PDF-1.7\x00\xff binary"

    email_service.send_report_email(
        to=ADDRESS, topic="Árazás", run_id=RUN_ID, pdf=pdf
    )

    assert len(sent) == 1
    payload = sent[0]
    assert payload["from"] == "demo@example.test"
    assert payload["to"] == [ADDRESS]
    assert payload["subject"] and payload["html"]
    (attachment,) = payload["attachments"]
    assert attachment["filename"] == f"swarmsense-{RUN_ID[:8]}.pdf"
    assert base64.b64decode(attachment["content"]) == pdf


def test_send_error_message_has_no_provider_text(monkeypatch):
    def failing(payload: dict) -> None:
        raise email_service.EmailSendError("HTTP 422")

    monkeypatch.setattr(email_service, "_post_resend", failing)

    with pytest.raises(email_service.EmailSendError) as info:
        email_service.send_report_email(
            to=ADDRESS, topic="Árazás", run_id=RUN_ID, pdf=b"%PDF"
        )

    assert ADDRESS not in str(info.value)
    assert str(info.value) == "HTTP 422"
