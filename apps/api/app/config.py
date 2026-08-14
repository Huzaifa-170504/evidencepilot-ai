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
    app_version: str = "1.0.0"
    app_env: str = "development"
    app_log_level: str = "INFO"
    frontend_origins: str = "http://localhost:5173"
    demo_mode: bool = True
    live_research_enabled: bool = False
    api_prefix: str = "/api/v1"
    max_question_length: int = Field(default=2_000, ge=100, le=20_000)
    max_upload_bytes: int = Field(default=10 * 1024 * 1024, ge=1024)
    max_pdf_pages: int = Field(default=150, ge=1, le=1000)
    max_public_runs_per_day: int = Field(default=1, ge=0, le=1000)
    request_timeout_seconds: float = Field(default=30.0, ge=1, le=120)

    supabase_url: str = ""
    supabase_publishable_key: str = ""
    supabase_service_role_key: str = ""
    database_url: str = ""

    llm_provider: str = "deterministic"
    llm_model: str = "gemini-2.5-flash-lite"
    embedding_provider: str = "hashing"
    embedding_model: str = "gemini-embedding-001"
    gemini_api_key: str = ""
    tavily_api_key: str = ""

    storage_bucket: str = "research-documents"
    embedding_dimensions: int = Field(default=384, ge=64, le=3072)

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.frontend_origins.split(",") if origin.strip()]

    @property
    def supabase_enabled(self) -> bool:
        return bool(self.supabase_url and self.supabase_publishable_key)

    @property
    def provider_mode(self) -> str:
        if self.live_research_enabled and self.gemini_api_key:
            return self.llm_provider
        return "deterministic"


@lru_cache
def get_settings() -> Settings:
    return Settings()
