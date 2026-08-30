from app.models.company import Company
from app.models.enums import EmploymentType, ParserType
from app.scrapers.types import JobPosting
from app.services import job_service
from app.services.matcher import MatchResult
from tests.conftest import requires_db

pytestmark = requires_db


def _job(db) -> int:
    company = Company(
        name="Acme",
        career_url="https://boards.greenhouse.io/acme",
        parser_type=ParserType.GREENHOUSE,
    )
    db.add(company)
    db.flush()
    posting = JobPosting(
        source="greenhouse",
        external_id="1",
        title="Backend Engineer",
        location="Pune, India",
        employment_type=EmploymentType.FULL_TIME,
        apply_url="https://example.com/1",
    )
    job, _ = job_service.upsert_job(
        db, company, posting,
        MatchResult(is_relevant=True, score=70, matched_roles=["backend"], country="India"),
    )
    return job.id


def test_save_then_apply_then_remove(api_client, db_session):
    job_id = _job(db_session)

    saved = api_client.put(f"/api/v1/saved-jobs/{job_id}", json={"status": "saved"})
    assert saved.status_code == 200
    assert saved.json()["job"]["title"] == "Backend Engineer"

    applied = api_client.put(f"/api/v1/saved-jobs/{job_id}", json={"status": "applied"})
    assert applied.json()["status"] == "applied"
    assert applied.json()["id"] == saved.json()["id"]  # upsert, not a new row

    applied_list = api_client.get("/api/v1/saved-jobs", params={"status": "applied"}).json()
    assert applied_list[0]["job_id"] == job_id
    assert api_client.get("/api/v1/saved-jobs", params={"status": "saved"}).json() == []

    assert api_client.delete(f"/api/v1/saved-jobs/{job_id}").status_code == 204
    assert api_client.get("/api/v1/saved-jobs").json() == []


def test_save_missing_job_is_404(api_client):
    assert api_client.put("/api/v1/saved-jobs/999", json={"status": "saved"}).status_code == 404
    assert api_client.delete("/api/v1/saved-jobs/999").status_code == 404
