from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=(".env", "../../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "EvidencePilot AI API"
    app_version: str = "0.1.0"
    app_env: str = "development"
    app_log_level: str = "INFO"
    frontend_origins: str = "http://localhost:5173"
    demo_mode: bool = True
    api_prefix: str = "/api/v1"
    max_question_length: int = Field(default=2_000, ge=100, le=20_000)

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.frontend_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
