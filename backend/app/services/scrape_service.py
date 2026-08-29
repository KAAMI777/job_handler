"""Orchestrates a full scrape: every active company -> postings -> matched jobs.

Two callers:
- the API (``POST /scrape/run``) schedules :func:`execute_run` as a background task;
- the standalone runner (``python -m app.scrape_runner``, for a Render Cron Job) calls
  :func:`run_scrape_now`, which blocks until the run finishes.

Both go through :func:`start_run`, so only one run is ever in flight.
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime, timedelta

import httpx
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.company import Company
from app.models.enums import RunStatus, RunType
from app.models.scrape_run import ScrapeRun
from app.scrapers import ScraperError, get_scraper_class
from app.services import job_service
from app.services.matcher import RuleMap, evaluate, load_rules

logger = logging.getLogger(__name__)

# Large batches (many Workday/enterprise companies) can legitimately run long, so this
# is generous. Runs still stuck after this are treated as crashed.
STALE_RUN_AFTER = timedelta(hours=3)


def _now() -> datetime:
    return datetime.now(UTC)


def reap_stale_runs(db: Session) -> None:
    """Fail runs left ``running`` by a crashed worker so they stop blocking new ones."""
    cutoff = _now() - STALE_RUN_AFTER
    stale = db.scalars(
        select(ScrapeRun).where(
            ScrapeRun.status == RunStatus.RUNNING, ScrapeRun.started_at < cutoff
        )
    )
    for run in stale:
        run.status = RunStatus.FAILED
        run.finished_at = _now()
    db.commit()


def active_run(db: Session) -> ScrapeRun | None:
    return db.scalar(select(ScrapeRun).where(ScrapeRun.status == RunStatus.RUNNING))


def get_run(db: Session, run_id: int) -> ScrapeRun | None:
    return db.get(ScrapeRun, run_id)


def list_runs(db: Session, *, limit: int = 20) -> list[ScrapeRun]:
    stmt = select(ScrapeRun).order_by(ScrapeRun.started_at.desc()).limit(limit)
    return list(db.scalars(stmt))


def create_run(db: Session, run_type: RunType) -> ScrapeRun:
    run = ScrapeRun(run_type=run_type, status=RunStatus.RUNNING, started_at=_now())
    db.add(run)
    db.commit()
    db.refresh(run)
    return run


def start_run(db: Session, run_type: RunType) -> ScrapeRun | None:
    """Reap stale runs, then create a new one unless another is already running.

    Returns the new run, or ``None`` if a run is already in progress.
    """
    reap_stale_runs(db)
    if active_run(db) is not None:
        return None
    return create_run(db, run_type)


def run_scrape_now(run_type: RunType = RunType.SCHEDULED) -> ScrapeRun | None:
    """Start and fully execute a run in the current process (blocking).

    Used by the standalone runner. Returns the finished run, or ``None`` if one was
    already in progress.
    """
    db = SessionLocal()
    try:
        run = start_run(db, run_type)
    finally:
        db.close()

    if run is None:
        logger.info("Scrape skipped: a run is already in progress")
        return None

    execute_run(run.id)

    db = SessionLocal()
    try:
        return db.get(ScrapeRun, run.id)
    finally:
        db.close()


def execute_run(run_id: int) -> None:
    """Entry point for the background task."""
    db = SessionLocal()
    try:
        _execute(db, run_id)
    except Exception:  # noqa: BLE001 - last-resort guard so a run never stays "running"
        logger.exception("Scrape run %s crashed", run_id)
        db.rollback()
        run = db.get(ScrapeRun, run_id)
        if run is not None:
            run.status = RunStatus.FAILED
            run.finished_at = _now()
            db.commit()
    finally:
        db.close()


def _execute(db: Session, run_id: int) -> None:
    run = db.get(ScrapeRun, run_id)
    if run is None:
        logger.error("Scrape run %s not found", run_id)
        return

    rules = load_rules(db)
    companies = list(db.scalars(select(Company).where(Company.active.is_(True))))

    checked = new_jobs = failed = 0

    for company in companies:
        try:
            created = _scrape_company(db, company, rules)
        except (ScraperError, httpx.HTTPError) as exc:
            failed += 1
            company.last_status = f"error: {exc}"[:50]
            company.consecutive_failures += 1
            company.last_scraped_at = _now()
            db.commit()
            logger.warning("Company %s (%s) failed: %s", company.id, company.name, exc)
            continue

        checked += 1
        new_jobs += created
        company.last_status = "ok"
        company.consecutive_failures = 0
        company.last_scraped_at = _now()
        db.commit()

    finished = _now()
    run.companies_checked = checked
    run.new_jobs = new_jobs
    run.failed = failed
    run.finished_at = finished
    run.duration_seconds = round((finished - run.started_at).total_seconds(), 2)
    run.status = _final_status(checked, failed)
    db.commit()
    logger.info(
        "Scrape run %s done: checked=%s new=%s failed=%s in %ss",
        run_id,
        checked,
        new_jobs,
        failed,
        run.duration_seconds,
    )


def _scrape_company(db: Session, company: Company, rules: RuleMap) -> int:
    scraper_cls = get_scraper_class(company.parser_type)
    with scraper_cls() as scraper:
        postings = scraper.scrape(company.career_url)

    created_count = 0
    seen: set[str] = set()
    for posting in postings:
        match = evaluate(posting, rules)
        job, created = job_service.upsert_job(db, company, posting, match)
        seen.add(job.job_hash)
        created_count += int(created)

    job_service.deactivate_missing(db, company.id, seen)
    return created_count


def _final_status(checked: int, failed: int) -> RunStatus:
    if failed == 0:
        return RunStatus.SUCCESS
    if checked == 0:
        return RunStatus.FAILED
    return RunStatus.PARTIAL
