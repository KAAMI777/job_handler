from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import SavedStatus, pg_enum
from app.models.mixins import TimestampMixin


class SavedJob(TimestampMixin, Base):
    """A job the user has starred or marked as applied.

    Single-user today. ``user_id`` is reserved (nullable) for when accounts land;
    the unique constraint is on ``job_id`` alone until then.
    """

    __tablename__ = "saved_jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    job_id: Mapped[int] = mapped_column(
        ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    user_id: Mapped[int | None] = mapped_column(Integer)
    status: Mapped[SavedStatus] = mapped_column(
        pg_enum(SavedStatus, "saved_status"), nullable=False, default=SavedStatus.SAVED
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    job: Mapped["Job"] = relationship()  # noqa: F821
