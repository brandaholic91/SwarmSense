from __future__ import annotations

import resend

from app.core.config import get_settings


def send_magic_link_email(recipient_email: str, verify_url: str) -> None:
    settings = get_settings()
    resend.api_key = settings.resend_api_key

    resend.Emails.send(
        {
            "from": settings.email_from,
            "to": [recipient_email],
            "reply_to": settings.email_reply_to,
            "subject": "SwarmSense - Bejelentkezesi link",
            "html": (
                "<div style='font-family:Arial,sans-serif;line-height:1.6;'>"
                "<h2>Folytasd a SwarmSense elemzest</h2>"
                "<p>Kattints a lenti gombra az azonositashoz.</p>"
                f"<p><a href='{verify_url}'>Bejelentkezes magic linkkel</a></p>"
                "<p>Ez a link 24 oran belul lejar.</p>"
                "</div>"
            ),
        }
    )
