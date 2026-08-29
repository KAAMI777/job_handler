from app.models.enums import RunStatus, RunType
from app.services import scrape_service
from app.services.scrape_service import create_run, start_run
from tests.conftest import requires_db

pytestmark = requires_db


def test_start_run_refuses_when_one_is_active(db_session):
    first = start_run(db_session, RunType.SCHEDULED)
    assert first is not None

    second = start_run(db_session, RunType.SCHEDULED)
    assert second is None


def test_start_run_reaps_stale_then_starts(db_session, monkeypatch):
    stale = create_run(db_session, RunType.SCHEDULED)

    # Pretend the stale run started long before the staleness cutoff.
    from datetime import UTC, datetime, timedelta

    stale.started_at = datetime.now(UTC) - timedelta(hours=4)
    db_session.commit()

    fresh = start_run(db_session, RunType.SCHEDULED)
    assert fresh is not None and fresh.id != stale.id

    db_session.refresh(stale)
    assert stale.status is RunStatus.FAILED


def test_runner_main_returns_zero_on_success(db_session, monkeypatch):
    # No companies -> run finishes immediately with status SUCCESS.
    monkeypatch.setattr(scrape_service, "SessionLocal", lambda: db_session)
    monkeypatch.setattr(db_session, "close", lambda: None)

    from app.scrape_runner import main

    assert main() == 0
