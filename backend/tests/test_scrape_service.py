from sqlalchemy import select

from app.models.company import Company
from app.models.enums import ParserType, RunStatus, RunType
from app.models.job import Job
from app.scrapers.types import JobPosting
from app.services import scrape_service
from app.services.scrape_service import create_run
from tests.conftest import requires_db

pytestmark = requires_db


class _FakeScraper:
    def __init__(self, postings):
        self._postings = postings

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return None

    def scrape(self, career_url):
        return self._postings


def _company(db, **kw) -> Company:
    defaults = {
        "name": "Acme",
        "career_url": "https://boards.greenhouse.io/acme",
        "parser_type": ParserType.GREENHOUSE,
        "active": True,
    }
    company = Company(**{**defaults, **kw})
    db.add(company)
    db.flush()
    return company


def _posting(**kw) -> JobPosting:
    base = {
        "source": "greenhouse",
        "external_id": "1",
        "title": "Backend Engineer",
        "location": "Bengaluru, India",
        "employment_type": "full_time",
        "apply_url": "https://boards.greenhouse.io/acme/jobs/1",
    }
    return JobPosting(**{**base, **kw})


def test_execute_run_scrapes_matches_and_tallies(db_session, monkeypatch):
    company = _company(db_session)
    # One relevant India job, one US job that is stored but not relevant.
    postings = [
        _posting(),
        _posting(external_id="2", location="Austin, TX", title="Backend Engineer"),
    ]
    monkeypatch.setattr(
        scrape_service, "get_scraper_class", lambda pt: lambda: _FakeScraper(postings)
    )

    run = create_run(db_session, RunType.MANUAL)
    scrape_service._execute(db_session, run.id)

    db_session.refresh(run)
    assert run.status is RunStatus.SUCCESS
    assert run.companies_checked == 1
    assert run.new_jobs == 2
    assert run.failed == 0
    assert run.duration_seconds is not None

    jobs = db_session.scalars(select(Job).where(Job.company_id == company.id)).all()
    assert {j.is_relevant for j in jobs} == {True, False}

    company_after = db_session.get(Company, company.id)
    assert company_after.last_status == "ok"
    assert company_after.consecutive_failures == 0


def test_execute_run_records_per_company_failure(db_session, monkeypatch):
    _company(db_session)

    def boom():
        raise scrape_service.ScraperError("no board")

    monkeypatch.setattr(scrape_service, "get_scraper_class", lambda pt: boom)

    run = create_run(db_session, RunType.SCHEDULED)
    scrape_service._execute(db_session, run.id)

    db_session.refresh(run)
    assert run.status is RunStatus.FAILED
    assert run.failed == 1
    assert run.companies_checked == 0


def test_second_upsert_does_not_count_as_new(db_session, monkeypatch):
    _company(db_session)
    monkeypatch.setattr(
        scrape_service, "get_scraper_class", lambda pt: lambda: _FakeScraper([_posting()])
    )

    run1 = create_run(db_session, RunType.SCHEDULED)
    scrape_service._execute(db_session, run1.id)
    run2 = create_run(db_session, RunType.SCHEDULED)
    scrape_service._execute(db_session, run2.id)

    db_session.refresh(run2)
    assert run2.new_jobs == 0
