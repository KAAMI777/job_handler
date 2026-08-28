from app.models.company import Company
from app.models.enums import EmploymentType, ParserType
from app.scrapers.types import JobPosting
from app.services import job_service
from app.services.matcher import MatchResult
from tests.conftest import requires_db

pytestmark = requires_db

RELEVANT = MatchResult(is_relevant=True, score=40, matched_roles=["backend"], country="India")


def _company(db) -> Company:
    company = Company(
        name="Acme",
        career_url="https://boards.greenhouse.io/acme",
        parser_type=ParserType.GREENHOUSE,
    )
    db.add(company)
    db.flush()
    return company


def _posting(**kw) -> JobPosting:
    base = {
        "source": "greenhouse",
        "external_id": "req-1",
        "title": "Backend Engineer",
        "location": "Pune, India",
        "employment_type": EmploymentType.FULL_TIME,
        "apply_url": "https://boards.greenhouse.io/acme/jobs/1",
    }
    return JobPosting(**{**base, **kw})


def test_insert_then_update_in_place(db_session):
    company = _company(db_session)

    job, created = job_service.upsert_job(db_session, company, _posting(), RELEVANT)
    assert created is True
    assert job.is_relevant and job.score == 40
    first_seen = job.first_seen_at

    job2, created2 = job_service.upsert_job(
        db_session, company, _posting(title="Senior Backend Engineer"), RELEVANT
    )
    assert created2 is False
    assert job2.id == job.id
    assert job2.title == "Senior Backend Engineer"
    assert job2.first_seen_at == first_seen
    assert job2.last_seen_at >= first_seen


def test_deactivate_missing(db_session):
    company = _company(db_session)
    kept, _ = job_service.upsert_job(db_session, company, _posting(external_id="a"), RELEVANT)
    gone, _ = job_service.upsert_job(db_session, company, _posting(external_id="b"), RELEVANT)

    affected = job_service.deactivate_missing(db_session, company.id, {kept.job_hash})
    assert affected == 1

    db_session.refresh(gone)
    db_session.refresh(kept)
    assert gone.is_active is False
    assert kept.is_active is True
