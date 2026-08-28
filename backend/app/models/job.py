from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import EmploymentType, pg_enum
from app.models.mixins import TimestampMixin


class Job(TimestampMixin, Base):
    __tablename__ = "jobs"
    __table_args__ = (
        Index("ix_jobs_company_id", "company_id"),
        Index("ix_jobs_created_at", "created_at"),
        Index("ix_jobs_score", "score"),
        Index("ix_jobs_relevant_active", "is_relevant", "is_active"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # Deterministic dedup key; see app/utils/hashing.py for composition.
    job_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)

    company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"), nullable=False
    )

    # Provenance from the source ATS.
    source: Mapped[str | None] = mapped_column(String(50))
    external_id: Mapped[str | None] = mapped_column(String(200))

    title: Mapped[str] = mapped_column(String(300), nullable=False)
    location: Mapped[str | None] = mapped_column(String(300))
    country: Mapped[str | None] = mapped_column(String(100))
    employment_type: Mapped[EmploymentType | None] = mapped_column(
        pg_enum(EmploymentType, "employment_type")
    )
    apply_url: Mapped[str] = mapped_column(String(1000), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)

    # Matching results.
    is_relevant: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="false"
    )
    score: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    matched_roles: Mapped[list[str]] = mapped_column(
        JSONB, nullable=False, default=list, server_default="[]"
    )
    scored_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # Lifecycle across scrape runs.
    first_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    last_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default="true"
    )

    company: Mapped["Company"] = relationship(back_populates="jobs")  # noqa: F821
