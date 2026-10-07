"""Discord-értesítések: elbukott futás, betelt napi keret.

A webhook-cím titok, ezért a hibáról csak a kivétel típusa kerül a naplóba, és az
üzenetben nincs a kérdés vagy a célközönség szövege."""

from __future__ import annotations

import json
import logging
from urllib.request import Request, urlopen

from app.core.config import get_settings

USER_AGENT = "swarmsense/0.1"
TIMEOUT_SECONDS = 10

logger = logging.getLogger("swarmsense.notify")


def notify_run_failed(run_id: str, error_code: str) -> None:
    base = str(get_settings().public_base_url).rstrip("/")
    _notify(
        "SwarmSense: elbukott egy futás\n"
        f"Futás: {run_id}\n"
        f"Hibakód: {error_code}\n"
        f"{base}/eredmeny/{run_id}"
    )


def notify_daily_limit_reached() -> None:
    limit = get_settings().runs_per_day
    _notify(f"SwarmSense: betelt a napi futáskeret ({limit} futás 24 óra alatt).")


def _notify(content: str) -> None:
    if not get_settings().discord_webhook_url:
        return
    try:
        _post_discord(content)
    except Exception as exc:
        logger.error("discord notification failed: %s", type(exc).__name__)


def _post_discord(content: str) -> None:
    request = Request(
        url=get_settings().discord_webhook_url,
        data=json.dumps({"content": content}).encode("utf-8"),
        headers={"Content-Type": "application/json", "User-Agent": USER_AGENT},
        method="POST",
    )
    # a hibákat a hívó kezeli (típus-szintű napló); a címet nem tesszük üzenetbe
    with urlopen(request, timeout=TIMEOUT_SECONDS) as response:
        response.read()
