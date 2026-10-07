from __future__ import annotations

import asyncio
import time

import pytest
from fastapi.testclient import TestClient

from app.services import cleanup


def test_cleanup_runs_once_at_startup(clean_db, monkeypatch):
    calls: list[int] = []
    monkeypatch.setattr(cleanup, "fail_stuck_runs_once", lambda: calls.append(1) or 0)
    monkeypatch.setattr(cleanup, "delete_old_emails_once", lambda: 0)
    from app.main import create_app

    with TestClient(create_app()):
        deadline = time.monotonic() + 5
        while not calls and time.monotonic() < deadline:
            time.sleep(0.01)
        assert calls == [1]


def test_cleanup_task_is_cancelled_on_shutdown(clean_db, monkeypatch):
    events: list[str] = []

    async def fake_loop(**_) -> None:
        events.append("started")
        try:
            await asyncio.sleep(3600)
        except asyncio.CancelledError:
            events.append("cancelled")
            raise

    monkeypatch.setattr(cleanup, "cleanup_loop", fake_loop)
    from app.main import create_app

    with TestClient(create_app()):
        pass
    assert events == ["started", "cancelled"]


@pytest.mark.parametrize(
    "name",
    [
        "max_concurrent_runs",
        "runs_per_ip_per_day",
        "runs_per_day",
        "emails_per_run",
        "emails_per_day",
    ],
)
def test_negative_limit_setting_is_rejected(monkeypatch, name):
    from pydantic import ValidationError

    from app.core.config import Settings

    monkeypatch.setenv(f"SWARMSENSE_{name.upper()}", "-1")
    with pytest.raises(ValidationError):
        Settings()

    monkeypatch.setenv(f"SWARMSENSE_{name.upper()}", "0")
    assert getattr(Settings(), name) == 0
