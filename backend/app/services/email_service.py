"""A jelentés PDF-jének elküldése Resenden keresztül."""

from __future__ import annotations

import base64
import html
import http.client
import json
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from app.core.config import get_settings

RESEND_URL = "https://api.resend.com/emails"
USER_AGENT = "swarmsense/0.1"
TIMEOUT_SECONDS = 30


class EmailSendError(Exception):
    """A küldés elbukott; az üzenet csak HTTP-státusz vagy kivételtípus-név."""


def build_email(*, topic: str, run_id: str) -> tuple[str, str]:
    """Tárgy és HTML törzs. A kérdés escape-elve kerül a törzsbe."""
    base = str(get_settings().public_base_url).rstrip("/")
    link = f"{base}/eredmeny/{run_id}"
    subject = "SwarmSense jelentés: a kérdésed eredménye"
    body = (
        "<p>Ezt a kérdést vizsgáltuk:</p>"
        f"<p><strong>{html.escape(topic)}</strong></p>"
        f'<p>Az eredmény az oldalon is megnyitható: <a href="{html.escape(link)}">'
        f"{html.escape(link)}</a></p>"
        "<p>A jelentés PDF-ben csatolva van. Ezt a levelet az oldalon kérted, "
        "és más levél nem érkezik.</p>"
    )
    return subject, body


def send_report_email(*, to: str, topic: str, run_id: str, pdf: bytes) -> None:
    settings = get_settings()
    subject, body = build_email(topic=topic, run_id=run_id)
    _post_resend(
        {
            "from": settings.email_from,
            "to": [to],
            "subject": subject,
            "html": body,
            "attachments": [
                {
                    "filename": f"swarmsense-{run_id[:8]}.pdf",
                    "content": base64.b64encode(pdf).decode("ascii"),
                }
            ],
        }
    )


def _post_resend(payload: dict[str, Any]) -> None:
    headers = {
        "Authorization": f"Bearer {get_settings().resend_api_key}",
        "Content-Type": "application/json",
        "User-Agent": USER_AGENT,
    }
    request = Request(
        url=RESEND_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    try:
        with urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            response.read()
    except HTTPError as exc:
        # a szolgáltató hibaüzenete a címzettet is visszhangozhatja: csak a státusz megy tovább
        raise EmailSendError(f"HTTP {exc.code}") from None
    except URLError as exc:
        raise EmailSendError(type(exc.reason).__name__) from None
    except (OSError, http.client.HTTPException) as exc:
        raise EmailSendError(type(exc).__name__) from None
