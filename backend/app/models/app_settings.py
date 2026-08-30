from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

SETTINGS_ROW_ID = 1


class AppSettings(Base):
    """A single mutable row (id = 1) for settings the user edits from the UI.

    Anything unset here falls back to the environment (`app.core.config.Settings`).
    """

    __tablename__ = "app_settings"
    __table_args__ = (CheckConstraint("id = 1", name="ck_app_settings_singleton"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=SETTINGS_ROW_ID)
    notify_min_score: Mapped[int | None] = mapped_column(Integer)
    notify_email: Mapped[str | None] = mapped_column(String(500))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
