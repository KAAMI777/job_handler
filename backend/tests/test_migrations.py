import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect

from app.core.config import get_settings

DATABASE_URL = get_settings().database_url

pytestmark = pytest.mark.skipif(
    not DATABASE_URL.startswith("postgresql"),
    reason="Migration test needs a Postgres DATABASE_URL (enum/JSONB types).",
)

EXPECTED_TABLES = {"companies", "jobs", "scrape_runs", "keyword_rules"}


def _alembic_config() -> Config:
    return Config("alembic.ini")


def test_upgrade_then_downgrade_is_clean():
    cfg = _alembic_config()
    command.downgrade(cfg, "base")
    command.upgrade(cfg, "head")

    engine = create_engine(DATABASE_URL)
    tables = set(inspect(engine).get_table_names())
    assert EXPECTED_TABLES.issubset(tables)

    # Re-running the full cycle must not raise (enum types dropped/recreated cleanly).
    command.downgrade(cfg, "base")
    command.upgrade(cfg, "head")
    engine.dispose()
