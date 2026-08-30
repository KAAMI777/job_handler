from dataclasses import dataclass

import httpx

from app.models.company import Company
from app.models.enums import ParserType, RunType
from app.scrapers.types import JobPosting
from app.services import job_service, notify_service, settings_service
from app.services.matcher import MatchResult
from app.services.scrape_service import create_run
from app.services.settings_service import Recipient
from tests.conftest import requires_db

pytestmark = requires_db


@dataclass
class _FakeEnv:
    resend_api_key: str | None = "re_test"
    notify_from_email: str = "onboarding@resend.dev"


def _configure(
    monkeypatch, *, resend_api_key="re_test", recipients=None, min_score=0
):
    monkeypatch.setattr(
        notify_service, "get_settings", lambda: _FakeEnv(resend_api_key=resend_api_key)
    )
    if recipients is None:
        recipients = [Recipient(email="me@example.com", min_score=min_score)]
    monkeypatch.setattr(settings_service, "digest_recipients", lambda db: recipients)


def _seed_relevant_job(db, *, title="Backend Engineer", company_name="Acme"):
    company = Company(
        name=company_name,
        career_url=f"https://boards.greenhouse.io/{company_name.lower()}",
        parser_type=ParserType.GREENHOUSE,
    )
    db.add(company)
    db.flush()
    posting = JobPosting(
        source="greenhouse",
        external_id="1",
        title=title,
        location="Bengaluru, India",
        apply_url="https://example.com/apply/1",
        description="<p>Great role</p>",
    )
    job_service.upsert_job(
        db,
        company,
        posting,
        MatchResult(is_relevant=True, score=60, matched_roles=["backend"], country="India"),
    )


def test_skips_when_not_configured(db_session, monkeypatch):
    _configure(monkeypatch, resend_api_key=None)
    run = create_run(db_session, RunType.SCHEDULED)
    assert notify_service.send_new_jobs_digest(db_session, run) is False


def test_skips_when_no_new_relevant_jobs(db_session, monkeypatch):
    _configure(monkeypatch)
    run = create_run(db_session, RunType.SCHEDULED)
    assert notify_service.send_new_jobs_digest(db_session, run) is False


def test_sends_grouped_digest(db_session, monkeypatch):
    run = create_run(db_session, RunType.SCHEDULED)
    _seed_relevant_job(db_session, title="Senior Backend Engineer", company_name="Acme")
    _seed_relevant_job(db_session, title="Platform Engineer", company_name="Beta")

    _configure(monkeypatch)
    sent = {}

    def fake_post(url, headers, json, timeout):
        sent["url"] = url
        sent["json"] = json
        return httpx.Response(200, json={"id": "email_1"}, request=httpx.Request("POST", url))

    monkeypatch.setattr(notify_service.httpx, "post", fake_post)

    assert notify_service.send_new_jobs_digest(db_session, run) is True
    assert sent["url"] == notify_service.RESEND_ENDPOINT
    body = sent["json"]
    assert body["to"] == ["me@example.com"]
    assert "2 new software job(s)" in body["subject"]
    assert "Acme (1)" in body["text"] and "Beta (1)" in body["text"]
    assert "Senior Backend Engineer" in body["text"]
    assert "[backend]" in body["text"]
    assert "https://example.com/apply/1" in body["text"]


def test_each_recipient_filtered_by_their_own_min_score(db_session, monkeypatch):
    run = create_run(db_session, RunType.SCHEDULED)
    _seed_relevant_job(db_session, title="Backend Engineer", company_name="Acme")  # score 60

    _configure(
        monkeypatch,
        recipients=[
            Recipient(email="all@example.com", min_score=0),
            Recipient(email="picky@example.com", min_score=80),
        ],
    )
    sent_to = []
    monkeypatch.setattr(
        notify_service.httpx,
        "post",
        lambda url, headers, json, timeout: sent_to.append(json["to"][0])
        or httpx.Response(200, json={"id": "x"}, request=httpx.Request("POST", url)),
    )

    assert notify_service.send_new_jobs_digest(db_session, run) is True
    assert sent_to == ["all@example.com"]


def test_http_error_does_not_raise(db_session, monkeypatch):
    run = create_run(db_session, RunType.SCHEDULED)
    _seed_relevant_job(db_session)
    _configure(monkeypatch)

    def boom(*a, **k):
        raise httpx.ConnectError("nope")

    monkeypatch.setattr(notify_service.httpx, "post", boom)
    assert notify_service.send_new_jobs_digest(db_session, run) is False
