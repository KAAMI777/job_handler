from pydantic import BaseModel, Field


class SettingsRead(BaseModel):
    """Effective settings — the DB row merged over environment defaults."""

    notify_min_score: int
    notify_email: str | None


class SettingsUpdate(BaseModel):
    notify_min_score: int | None = Field(default=None, ge=0, le=100)
    notify_email: str | None = None
