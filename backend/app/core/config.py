from __future__ import annotations

from functools import lru_cache

from pydantic import AnyHttpUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="SWARMSENSE_", case_sensitive=False)

    database_url: str = Field(...)
    llm_api_key: str = Field(...)
    llm_model: str = Field(default="deepseek-v4.1-flash")
    llm_base_url: AnyHttpUrl = Field(default="https://opencode.ai/zen/go/v1")
    internal_secret: str = Field(...)
    frontend_origin: AnyHttpUrl = Field(...)
    environment: str = Field(default="development")
    ip_hash_secret: str = Field(...)
    max_concurrent_runs: int = Field(default=2)
    runs_per_ip_per_day: int = Field(default=3)
    runs_per_day: int = Field(default=20)

    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()
