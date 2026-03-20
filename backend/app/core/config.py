from __future__ import annotations

from functools import lru_cache

from pydantic import AnyHttpUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="SWARMSENSE_", case_sensitive=False)

    supabase_url: AnyHttpUrl = Field(...)
    supabase_service_key: str = Field(...)
    kimi_api_key: str = Field(...)
    operator_api_key: str = Field(...)
    sentry_dsn: str | None = Field(default=None)
    environment: str = Field(default="development")
    frontend_origin: AnyHttpUrl = Field(...)

    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()
