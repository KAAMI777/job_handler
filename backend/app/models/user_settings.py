from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class UserSettings(Base):
    """Per-user notification preferences, keyed by the Supabase user id (JWT ``sub``).

    A row is created the first time a signed-in user loads their settings. The digest
    after each scrape run is sent to every row with ``notify_enabled`` true.
    When authentication is disabled there are no rows here and the legacy global
    ``app_settings.notify_email`` / ``NOTIFY_EMAIL`` is used instead.
    """

    __tablename__ = "user_settings"

    user_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    email: Mapped[str] = mapped_column(String(320), nullable=False)
    notify_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    # NULL -> fall back to the global app_settings / env minimum score.
    notify_min_score: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
