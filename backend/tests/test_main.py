from __future__ import annotations

import asyncio
import time

from fastapi.testclient import TestClient

from app.services import cleanup


def test_cleanup_runs_once_at_startup(clean_db, monkeypatch):
    calls: list[int] = []
    monkeypatch.setattr(
        cleanup,
        "run_cleanup_once",
        lambda: calls.append(1) or {"deleted_emails": 0, "failed_runs": 0},
    )
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
