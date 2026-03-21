from __future__ import annotations

import html
import json
from typing import Any

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
            "subject": "SwarmSense – Bejelentkezési link",
            "html": (
                "<div style='font-family:Arial,sans-serif;line-height:1.6;'>"
                "<h2>Folytasd a SwarmSense elemzést</h2>"
                "<p>Kattints a lenti gombra az azonosításhoz.</p>"
                f"<p><a href='{verify_url}'>Bejelentkezés magic linkkel</a></p>"
                "<p>Ez a link 24 órán belül lejár.</p>"
                "</div>"
            ),
        }
    )


def send_run_result_email(
    *, recipient_email: str, result_payload: dict[str, Any]
) -> None:
    settings = get_settings()
    resend.api_key = settings.resend_api_key

    persona_count = str(result_payload.get("persona_count_label", ""))
    compact_payload = html.escape(json.dumps(result_payload, ensure_ascii=False))
    resend.Emails.send(
        {
            "from": settings.email_from,
            "to": [recipient_email],
            "reply_to": settings.email_reply_to,
            "subject": f"SwarmSense run result ({persona_count})",
            "html": (
                "<div style='font-family:Arial,sans-serif;line-height:1.6;'>"
                f"<h2>Run summary ({persona_count})</h2>"
                "<p>Result payload for template processing:</p>"
                f"<pre>{compact_payload}</pre>"
                "</div>"
            ),
        }
    )
