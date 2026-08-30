"""add smartrecruiters parser type

Revision ID: 921ddb095d51
Revises: dfd3e78b7b21
Create Date: 2026-08-29

"""

from collections.abc import Sequence

from alembic import op

revision: str = "921ddb095d51"
down_revision: str | Sequence[str] | None = "dfd3e78b7b21"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

NEW_VALUES = ("smartrecruiters",)


def upgrade() -> None:
    # ALTER TYPE ... ADD VALUE cannot run inside a transaction block.
    with op.get_context().autocommit_block():
        for value in NEW_VALUES:
            op.execute(f"ALTER TYPE parser_type ADD VALUE IF NOT EXISTS '{value}'")


def downgrade() -> None:
    # Postgres has no "DROP VALUE" for enums; removing a value means recreating the
    # type. Left as a no-op — the extra values are harmless if unused.
    pass
