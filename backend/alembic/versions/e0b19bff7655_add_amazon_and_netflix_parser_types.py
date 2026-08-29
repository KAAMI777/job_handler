"""add amazon and netflix parser types

Revision ID: e0b19bff7655
Revises: 921ddb095d51
Create Date: 2026-08-29

"""

from collections.abc import Sequence

from alembic import op

revision: str = "e0b19bff7655"
down_revision: str | Sequence[str] | None = "921ddb095d51"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

NEW_VALUES = ("amazon", "netflix")


def upgrade() -> None:
    # ALTER TYPE ... ADD VALUE cannot run inside a transaction block.
    with op.get_context().autocommit_block():
        for value in NEW_VALUES:
            op.execute(f"ALTER TYPE parser_type ADD VALUE IF NOT EXISTS '{value}'")


def downgrade() -> None:
    # Postgres has no "DROP VALUE" for enums; left as a no-op.
    pass
