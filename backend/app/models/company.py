from datetime import datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import ParserType, pg_enum
from app.models.mixins import TimestampMixin


class Company(TimestampMixin, Base):
    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    career_url: Mapped[str] = mapped_column(String(500), unique=True, nullable=False)
    parser_type: Mapped[ParserType] = mapped_column(
        pg_enum(ParserType, "parser_type"), nullable=False
    )
    active: Mapped[bool] = mapped_column(nullable=False, default=True, server_default="true")

    # Scrape health, updated after each run.
    last_scraped_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_status: Mapped[str | None] = mapped_column(String(50))
    consecutive_failures: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default="0"
    )

    jobs: Mapped[list["Job"]] = relationship(  # noqa: F821
        back_populates="company", cascade="all, delete-orphan"
    )
