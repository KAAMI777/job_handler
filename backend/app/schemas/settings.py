from pydantic import BaseModel, Field


class SettingsRead(BaseModel):
    """Effective notification settings for the caller.

    For a signed-in user these come from their ``user_settings`` row (``notify_email`` is
    their account email, read-only). With auth disabled they are the global
    ``app_settings`` row merged over environment defaults.
    """

    notify_min_score: int
    notify_email: str | None
    notify_enabled: bool


class SettingsUpdate(BaseModel):
    notify_min_score: int | None = Field(default=None, ge=0, le=100)
    notify_enabled: bool | None = None
    # Only used when auth is disabled (global app_settings); ignored for a signed-in user,
    # whose digest address is their account email.
    notify_email: str | None = None
