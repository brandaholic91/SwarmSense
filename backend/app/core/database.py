from __future__ import annotations

from functools import lru_cache
from typing import TYPE_CHECKING

from app.core.config import get_settings

if TYPE_CHECKING:
    from supabase import Client


@lru_cache
def get_supabase_client() -> "Client":
    from supabase import create_client

    settings = get_settings()
    return create_client(str(settings.supabase_url), settings.supabase_service_key)
