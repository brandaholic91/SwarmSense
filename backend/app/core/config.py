from __future__ import annotations

from functools import lru_cache

from pydantic import AnyHttpUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="SWARMSENSE_", case_sensitive=False)

    supabase_url: AnyHttpUrl = Field(...)
    supabase_service_key: str = Field(...)
    kimi_api_key: str = Field(...)
    openrouter_api_key: str = Field(default="")
    openrouter_model: str = Field(default="moonshotai/kimi-k2")
    openrouter_base_url: str = Field(default="https://openrouter.ai/api/v1")
    operator_api_key: str = Field(...)
    internal_secret: str = Field(...)
    sentry_dsn: AnyHttpUrl | None = Field(default=None)
    environment: str = Field(default="development")
    frontend_origin: AnyHttpUrl = Field(...)
    resend_api_key: str = Field(...)
    email_from: str = Field(default="SwarmSense <noreply@swarmsense.ai>")
    email_reply_to: str = Field(default="support@swarmsense.ai")

    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()
