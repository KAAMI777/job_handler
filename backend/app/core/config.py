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

    # Authentication. When ``auth_enabled`` is False (the default) every API route is open,
    # matching the app's single-user origins. Flip it to True once the frontend signs users
    # in through Supabase and ``supabase_jwt_secret`` is set (Supabase dashboard ->
    # Project Settings -> API -> JWT Secret). ``service_token`` is an optional shared secret
    # that lets machine callers (the scheduled scrape in GitHub Actions / n8n) authenticate
    # with an ``X-Service-Token`` header instead of a user login.
    auth_enabled: bool = False
    supabase_jwt_secret: str | None = None  # legacy shared HS256 secret
    supabase_url: str | None = None  # e.g. https://<ref>.supabase.co — enables JWKS (ES256/RS256)
    # public anon key — lets the API call GoTrue for register / login
    supabase_anon_key: str | None = None
    service_token: str | None = None

    # Email digest of newly found relevant jobs after each scrape run.
    # All three must be set for mail to send; otherwise it is silently skipped.
    resend_api_key: str | None = None
    notify_email: str | None = None  # recipient(s), comma-separated
    notify_from_email: str = "onboarding@resend.dev"  # Resend's no-domain test sender
    notify_min_score: int = 0

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
