from sqlalchemy import Boolean, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import TimestampMixin


class KeywordRule(TimestampMixin, Base):
    """A single role/keyword pairing used by the matcher.

    Editable from the Settings page. ``role`` is a free string (e.g. "backend",
    "software_engineer") so new role buckets can be added without a migration.
    """

    __tablename__ = "keyword_rules"
    __table_args__ = (UniqueConstraint("role", "keyword", name="uq_keyword_rules_role_keyword"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    role: Mapped[str] = mapped_column(String(50), nullable=False)
    keyword: Mapped[str] = mapped_column(String(100), nullable=False)
    weight: Mapped[int] = mapped_column(Integer, nullable=False, default=1, server_default="1")
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default="true"
    )
