"""add companies.source_url

Revision ID: 6097344ac660
Revises: e0b19bff7655
Create Date: 2026-08-29 23:35:15.088909

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "6097344ac660"
down_revision: str | Sequence[str] | None = "e0b19bff7655"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("companies", sa.Column("source_url", sa.String(length=500), nullable=True))


def downgrade() -> None:
    op.drop_column("companies", "source_url")
