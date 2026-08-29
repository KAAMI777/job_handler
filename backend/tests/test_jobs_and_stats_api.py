from app.models.company import Company
from app.models.enums import EmploymentType, ParserType
from app.scrapers.types import JobPosting
from app.services import job_service
from app.services.matcher import MatchResult
from tests.conftest import requires_db

pytestmark = requires_db


def _seed(db):
    company = Company(
        name="Acme",
        career_url="https://boards.greenhouse.io/acme",
        parser_type=ParserType.GREENHOUSE,
    )
    db.add(company)
    db.flush()

    def posting(**kw):
        base = {
            "source": "greenhouse",
            "external_id": kw.get("external_id", "x"),
            "title": "Backend Engineer",
            "location": "Pune, India",
            "employment_type": EmploymentType.FULL_TIME,
            "apply_url": "https://boards.greenhouse.io/acme/jobs/x",
        }
        return JobPosting(**{**base, **kw})

    job_service.upsert_job(
        db, company, posting(external_id="1"),
        MatchResult(is_relevant=True, score=80, matched_roles=["backend"], country="India"),
    )
    job_service.upsert_job(
        db, company, posting(external_id="2", title="Frontend Engineer"),
        MatchResult(is_relevant=True, score=30, matched_roles=["frontend"], country="India"),
    )
    job_service.upsert_job(
        db, company, posting(external_id="3", title="Recruiter", location="Berlin"),
        MatchResult(is_relevant=False, score=0, matched_roles=[], country=None),
    )
    return company


def test_jobs_list_defaults_to_relevant_sorted_by_score(api_client, db_session):
    _seed(db_session)
    body = api_client.get("/api/v1/jobs").json()
    assert body["total"] == 2
    assert [j["title"] for j in body["items"]] == ["Backend Engineer", "Frontend Engineer"]


def test_jobs_list_filters(api_client, db_session):
    _seed(db_session)
    assert api_client.get("/api/v1/jobs", params={"min_score": 50}).json()["total"] == 1
    assert api_client.get("/api/v1/jobs", params={"role": "frontend"}).json()["total"] == 1
    assert api_client.get("/api/v1/jobs", params={"is_relevant": False}).json()["total"] == 1


def test_jobs_list_pagination(api_client, db_session):
    _seed(db_session)
    page = api_client.get("/api/v1/jobs", params={"limit": 1, "offset": 1}).json()
    assert page["limit"] == 1 and page["offset"] == 1
    assert len(page["items"]) == 1
    assert page["items"][0]["title"] == "Frontend Engineer"


def test_stats(api_client, db_session):
    _seed(db_session)
    stats = api_client.get("/api/v1/stats").json()
    assert stats["total_companies"] == 1
    assert stats["active_companies"] == 1
    assert stats["total_relevant_jobs"] == 2
    assert stats["jobs_today"] == 3
    assert stats["new_relevant_jobs_today"] == 2
