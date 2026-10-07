"""Futásesemények kiírása. Egy esemény elvesztése nem állíthatja meg a futást."""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Callable
from typing import Any

logger = logging.getLogger("swarmsense.run")

# hívása: sink(type, **fields)
EventSink = Callable[..., None]


async def safe_emit(sink: EventSink | None, type: str, **fields: Any) -> None:
    if sink is None:
        return
    try:
        await asyncio.to_thread(sink, type, **fields)
    except Exception as exc:
        # csak a kivétel típusa kerül a naplóba: az üzenet adatot tartalmazhat
        logger.error("event %s could not be written: %s", type, exc.__class__.__name__)
