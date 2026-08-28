from datetime import datetime

from sqlalchemy import DateTime, Integer, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.enums import RunStatus, RunType, pg_enum
from app.models.mixins import TimestampMixin


class ScrapeRun(TimestampMixin, Base):
    """One execution of the scrape pipeline. Backs the Phase 6 response and dashboard cards."""

    __tablename__ = "scrape_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    run_type: Mapped[RunType] = mapped_column(pg_enum(RunType, "run_type"), nullable=False)
    status: Mapped[RunStatus] = mapped_column(
        pg_enum(RunStatus, "run_status"),
        nullable=False,
        default=RunStatus.RUNNING,
        server_default=RunStatus.RUNNING.value,
    )

    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    companies_checked: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default="0"
    )
    new_jobs: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    failed: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    duration_seconds: Mapped[float | None] = mapped_column(Numeric(8, 2))
