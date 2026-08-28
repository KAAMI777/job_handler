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
        description="SQLAlchemy database URL, e.g. postgresql+psycopg2://user:pass@host/db",
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

    @property
    def is_production(self) -> bool:
        return self.environment == "production"


@lru_cache
def get_settings() -> Settings:
    """Return the cached settings instance."""
    return Settings()  # type: ignore[call-arg]
