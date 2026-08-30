"""add oracle and microsoft parser types

Revision ID: a12e34063f2c
Revises: 58c0bef1b6ae
Create Date: 2026-08-30

"""

from collections.abc import Sequence

from alembic import op

revision: str = "a12e34063f2c"
down_revision: str | Sequence[str] | None = "58c0bef1b6ae"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

NEW_VALUES = ("oracle", "microsoft")


def upgrade() -> None:
    with op.get_context().autocommit_block():
        for value in NEW_VALUES:
            op.execute(f"ALTER TYPE parser_type ADD VALUE IF NOT EXISTS '{value}'")


def downgrade() -> None:
    # Postgres has no "DROP VALUE" for enums; left as a no-op.
    pass
