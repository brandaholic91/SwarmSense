"""Takarítás: beragadt futások lezárása (percenként), lejárt e-mail-kérések törlése (óránként)."""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Callable

from app import db
from app.services import notifier

RUN_TIMED_OUT = "RUN_TIMED_OUT"

logger = logging.getLogger("swarmsense.cleanup")


def delete_old_emails_once() -> int:
    return db.delete_old_email_requests()


def fail_stuck_runs_once() -> int:
    stuck = db.fail_stuck_runs()
    for run_id in stuck:
        # egy futás hibája ne hagyja ki a többit (a lezárásuk már lefutott)
        try:
            db.insert_event(run_id, "run_failed", error_code=RUN_TIMED_OUT)
            notifier.notify_run_failed(run_id, RUN_TIMED_OUT)
        except Exception as exc:
            logger.error("cleanup of run %s failed: %s", run_id, type(exc).__name__)
    return len(stuck)


def run_cleanup_once() -> dict[str, int]:
    return {
        "deleted_emails": delete_old_emails_once(),
        "failed_runs": fail_stuck_runs_once(),
    }


async def _repeat(name: str, job: Callable[[], int], interval_seconds: float) -> None:
    """Azonnal fut egyszer, utána `interval_seconds`-enként. Egy kör hibája nem
    állítja le a ciklust; naplóba csak a kivétel típusa kerül."""
    while True:
        try:
            count = await asyncio.to_thread(job)
            logger.info("cleanup %s done: %s", name, count)
        except Exception as exc:
            logger.error("cleanup %s failed: %s", name, type(exc).__name__)
        await asyncio.sleep(interval_seconds)


async def cleanup_loop(
    *, interval_seconds: float = 3600, stuck_interval_seconds: float = 60
) -> None:
    """A beragadt futásokat percenként, a lejárt e-mail-kéréseket óránként
    takarítja; a két feladat egymástól függetlenül fut és bukik."""
    await asyncio.gather(
        _repeat("stuck runs", lambda: fail_stuck_runs_once(), stuck_interval_seconds),
        _repeat("old emails", lambda: delete_old_emails_once(), interval_seconds),
    )
