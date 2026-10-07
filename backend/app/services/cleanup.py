"""Óránkénti takarítás: lejárt e-mail-kérések törlése, beragadt futások lezárása."""

from __future__ import annotations

import asyncio
import logging

from app import db
from app.services import notifier

RUN_TIMED_OUT = "RUN_TIMED_OUT"

logger = logging.getLogger("swarmsense.cleanup")


def run_cleanup_once() -> dict[str, int]:
    deleted_emails = db.delete_old_email_requests()
    stuck = db.fail_stuck_runs()
    for run_id in stuck:
        db.insert_event(run_id, "run_failed", error_code=RUN_TIMED_OUT)
        notifier.notify_run_failed(run_id, RUN_TIMED_OUT)
    return {"deleted_emails": deleted_emails, "failed_runs": len(stuck)}


async def cleanup_loop(*, interval_seconds: float = 3600) -> None:
    """Azonnal fut egyszer, utána `interval_seconds`-enként. Egy kör hibája nem
    állítja le a ciklust; naplóba csak a kivétel típusa kerül."""
    while True:
        try:
            counts = await asyncio.to_thread(run_cleanup_once)
            logger.info("cleanup round done: %s", counts)
        except Exception as exc:
            logger.error("cleanup round failed: %s", type(exc).__name__)
        await asyncio.sleep(interval_seconds)
