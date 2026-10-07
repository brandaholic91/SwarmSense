from __future__ import annotations

from functools import lru_cache

from pydantic import AnyHttpUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="SWARMSENSE_", case_sensitive=False)

    database_url: str = Field(...)
    supabase_url: AnyHttpUrl = Field(...)
    supabase_service_key: str = Field(...)
    llm_api_key: str = Field(...)
    llm_model: str = Field(default="deepseek-v4.1-flash")
    llm_base_url: AnyHttpUrl = Field(default="https://opencode.ai/zen/go/v1")
    operator_api_key: str = Field(...)
    internal_secret: str = Field(...)
    sentry_dsn: AnyHttpUrl | None = Field(default=None)
    environment: str = Field(default="development")
    frontend_origin: AnyHttpUrl = Field(...)
    backend_origin: AnyHttpUrl = Field(...)
    resend_api_key: str = Field(...)
    email_from: str = Field(default="SwarmSense <noreply@em.swarmsense.hu>")
    email_reply_to: str = Field(default="support@swarmsense.hu")
    disable_single_run_limit: bool = Field(default=False)

    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()
