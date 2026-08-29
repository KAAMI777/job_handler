from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration, loaded from environment variables (and .env locally).

    Import via :func:`get_settings` so the object is parsed once and cached.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    environment: Literal["development", "staging", "production"] = "development"
    log_level: str = "INFO"

    database_url: str = Field(
        ...,
        description="Database URL. Bare postgres:// / postgresql:// URLs (as Supabase and "
        "Render hand them out) are rewritten to use the psycopg (v3) driver.",
    )

    # Comma-separated in the environment, e.g. "http://localhost:5173,https://app.example.com".
    cors_origins: list[str] = ["http://localhost:5173"]
    cors_origin_regex: str | None = r"https://job-handler-.*\.vercel\.app"

    @field_validator("cors_origins", mode="before")
    @classmethod
    def _split_cors_origins(cls, value: object) -> object:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @field_validator("database_url", mode="after")
    @classmethod
    def _use_psycopg_driver(cls, value: str) -> str:
        """Normalize Postgres URLs to the psycopg (v3) driver SQLAlchemy expects.

        ``postgres://`` and ``postgresql://`` -> ``postgresql+psycopg://``;
        an explicit ``postgresql+psycopg2://`` is also moved to psycopg v3.
        Non-Postgres URLs (e.g. sqlite in tests) pass through untouched.
        """
        for prefix in ("postgres://", "postgresql://", "postgresql+psycopg2://"):
            if value.startswith(prefix):
                return "postgresql+psycopg://" + value[len(prefix) :]
        return value

    @property
    def is_production(self) -> bool:
        return self.environment == "production"


@lru_cache
def get_settings() -> Settings:
    """Return the cached settings instance."""
    return Settings()  # type: ignore[call-arg]
