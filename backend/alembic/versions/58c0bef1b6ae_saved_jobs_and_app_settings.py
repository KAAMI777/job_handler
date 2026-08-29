"""saved_jobs and app_settings

Revision ID: 58c0bef1b6ae
Revises: 6097344ac660
Create Date: 2026-08-30

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "58c0bef1b6ae"
down_revision: str | Sequence[str] | None = "6097344ac660"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

saved_status = postgresql.ENUM("saved", "applied", name="saved_status", create_type=False)


def upgrade() -> None:
    saved_status.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "app_settings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("notify_min_score", sa.Integer(), nullable=True),
        sa.Column("notify_email", sa.String(length=500), nullable=True),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False
        ),
        sa.CheckConstraint("id = 1", name="ck_app_settings_singleton"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "saved_jobs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("job_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("status", saved_status, nullable=False),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False
        ),
        sa.ForeignKeyConstraint(["job_id"], ["jobs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("job_id"),
    )


def downgrade() -> None:
    op.drop_table("saved_jobs")
    op.drop_table("app_settings")
    saved_status.drop(op.get_bind(), checkfirst=True)
