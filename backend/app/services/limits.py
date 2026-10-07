"""Futásindítási keretek és a kliens-IP hash-elése."""

from __future__ import annotations

import hashlib
import hmac

from app import db
from app.core.config import get_settings
from app.core.errors import ErrorCode


def hash_ip(ip: str) -> str:
    """HMAC-SHA256 az `ip_hash_secret` kulccsal; nyers IP sehol nem tárolódik."""
    key = get_settings().ip_hash_secret.encode("utf-8")
    return hmac.new(key, ip.encode("utf-8"), hashlib.sha256).hexdigest()


def check_run_limits(ip_hash: str | None) -> ErrorCode | None:
    """Az első betelt keret kódja, vagy None. Sorrend: egyidejű, IP, napi."""
    settings = get_settings()
    if db.count_active_runs() >= settings.max_concurrent_runs:
        return ErrorCode.BUSY
    if (
        ip_hash is not None
        and db.count_runs_since(ip_hash=ip_hash)
        >= settings.runs_per_ip_per_day
    ):
        return ErrorCode.IP_LIMIT_REACHED
    if db.count_runs_since() >= settings.runs_per_day:
        return ErrorCode.DAILY_LIMIT_REACHED
    return None
