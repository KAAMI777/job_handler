"""seed default keyword rules

Starter keyword map for the matcher. Safe to edit or delete from the Settings page
afterwards; this migration only inserts rows that are not already present.

Revision ID: dfd3e78b7b21
Revises: d3eafa5a0e44
Create Date: 2026-08-29

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "dfd3e78b7b21"
down_revision: str | Sequence[str] | None = "d3eafa5a0e44"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

DEFAULT_RULES: dict[str, list[str]] = {
    "software_engineer": ["software engineer", "software developer", "swe", "sde"],
    "backend": ["backend", "back-end", "back end", "server-side", "api engineer"],
    "frontend": ["frontend", "front-end", "front end", "ui engineer"],
    "fullstack": ["fullstack", "full-stack", "full stack"],
    "platform": [
        "platform engineer",
        "infrastructure engineer",
        "devops",
        "site reliability",
        "sre",
    ],
}


def upgrade() -> None:
    keyword_rules = sa.table(
        "keyword_rules",
        sa.column("role", sa.String),
        sa.column("keyword", sa.String),
        sa.column("weight", sa.Integer),
        sa.column("is_active", sa.Boolean),
    )
    rows = [
        {"role": role, "keyword": keyword, "weight": 1, "is_active": True}
        for role, keywords in DEFAULT_RULES.items()
        for keyword in keywords
    ]
    op.bulk_insert(keyword_rules, rows)


def downgrade() -> None:
    roles = tuple(DEFAULT_RULES)
    op.execute(
        sa.text("DELETE FROM keyword_rules WHERE role IN :roles").bindparams(
            sa.bindparam("roles", roles, expanding=True)
        )
    )
