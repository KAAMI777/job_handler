"""initial schema

Revision ID: d3eafa5a0e44
Revises:
Create Date: 2026-08-29 04:21:14.216137

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "d3eafa5a0e44"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# Enum types are created/dropped explicitly so downgrade + re-upgrade is clean
# (a bare drop_table leaves the Postgres TYPE behind).
parser_type = postgresql.ENUM(
    "greenhouse", "lever", "ashby", "workday", "custom", name="parser_type", create_type=False
)
employment_type = postgresql.ENUM(
    "full_time", "part_time", "contract", "internship", "other",
    name="employment_type", create_type=False,
)
run_type = postgresql.ENUM("scheduled", "manual", name="run_type", create_type=False)
run_status = postgresql.ENUM(
    "running", "success", "partial", "failed", name="run_status", create_type=False
)

_ENUMS = (parser_type, employment_type, run_type, run_status)


def upgrade() -> None:
    bind = op.get_bind()
    for enum in _ENUMS:
        enum.create(bind, checkfirst=True)

    op.create_table(
        "companies",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("career_url", sa.String(length=500), nullable=False),
        sa.Column("parser_type", parser_type, nullable=False),
        sa.Column("active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("last_scraped_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_status", sa.String(length=50), nullable=True),
        sa.Column("consecutive_failures", sa.Integer(), server_default="0", nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("career_url"),
    )
    op.create_table(
        "keyword_rules",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("role", sa.String(length=50), nullable=False),
        sa.Column("keyword", sa.String(length=100), nullable=False),
        sa.Column("weight", sa.Integer(), server_default="1", nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("role", "keyword", name="uq_keyword_rules_role_keyword"),
    )
    op.create_table(
        "scrape_runs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("run_type", run_type, nullable=False),
        sa.Column("status", run_status, server_default="running", nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("companies_checked", sa.Integer(), server_default="0", nullable=False),
        sa.Column("new_jobs", sa.Integer(), server_default="0", nullable=False),
        sa.Column("failed", sa.Integer(), server_default="0", nullable=False),
        sa.Column("duration_seconds", sa.Numeric(precision=8, scale=2), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "jobs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("job_hash", sa.String(length=64), nullable=False),
        sa.Column("company_id", sa.Integer(), nullable=False),
        sa.Column("source", sa.String(length=50), nullable=True),
        sa.Column("external_id", sa.String(length=200), nullable=True),
        sa.Column("title", sa.String(length=300), nullable=False),
        sa.Column("location", sa.String(length=300), nullable=True),
        sa.Column("country", sa.String(length=100), nullable=True),
        sa.Column("employment_type", employment_type, nullable=True),
        sa.Column("apply_url", sa.String(length=1000), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_relevant", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("score", sa.Integer(), server_default="0", nullable=False),
        sa.Column(
            "matched_roles",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default="[]",
            nullable=False,
        ),
        sa.Column("scored_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "first_seen_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "last_seen_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False
        ),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("job_hash"),
    )
    op.create_index("ix_jobs_company_id", "jobs", ["company_id"], unique=False)
    op.create_index("ix_jobs_created_at", "jobs", ["created_at"], unique=False)
    op.create_index("ix_jobs_relevant_active", "jobs", ["is_relevant", "is_active"], unique=False)
    op.create_index("ix_jobs_score", "jobs", ["score"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_jobs_score", table_name="jobs")
    op.drop_index("ix_jobs_relevant_active", table_name="jobs")
    op.drop_index("ix_jobs_created_at", table_name="jobs")
    op.drop_index("ix_jobs_company_id", table_name="jobs")
    op.drop_table("jobs")
    op.drop_table("scrape_runs")
    op.drop_table("keyword_rules")
    op.drop_table("companies")

    bind = op.get_bind()
    for enum in _ENUMS:
        enum.drop(bind, checkfirst=True)
