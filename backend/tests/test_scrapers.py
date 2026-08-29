import json
from pathlib import Path

import httpx
import pytest

from app.models.enums import EmploymentType, ParserType
from app.scrapers import ScraperError, get_scraper_class
from app.scrapers.amazon import AmazonScraper
from app.scrapers.ashby import AshbyScraper
from app.scrapers.base import BaseScraper
from app.scrapers.greenhouse import GreenhouseScraper
from app.scrapers.lever import LeverScraper
from app.scrapers.netflix import NetflixScraper
from app.scrapers.normalize import normalize_employment_type
from app.scrapers.smartrecruiters import SmartRecruitersScraper
from app.scrapers.workday import WorkdayScraper

FIXTURES = Path(__file__).parent / "fixtures"


def _client(payload: object, *, status: int = 200, expect_url_contains: str | None = None):
    def handler(request: httpx.Request) -> httpx.Response:
        if expect_url_contains is not None:
            assert expect_url_contains in str(request.url)
        return httpx.Response(status, json=payload)

    return httpx.Client(transport=httpx.MockTransport(handler))


def _load(name: str) -> object:
    return json.loads((FIXTURES / name).read_text())


def test_greenhouse_parses_and_normalizes():
    scraper = GreenhouseScraper(_client(_load("greenhouse.json"), expect_url_contains="acme"))
    postings = scraper.scrape("https://boards.greenhouse.io/acme")

    assert [p.title for p in postings] == ["Senior Backend Engineer", "Marketing Intern"]
    first = postings[0]
    assert first.source == "greenhouse"
    assert first.external_id == "4012345"
    assert first.location == "Bengaluru, India"
    assert first.employment_type is EmploymentType.FULL_TIME
    assert first.apply_url.endswith("/jobs/4012345")
    assert postings[1].employment_type is EmploymentType.INTERNSHIP


def test_lever_parses_and_converts_timestamp():
    scraper = LeverScraper(_client(_load("lever.json"), expect_url_contains="/postings/beta"))
    postings = scraper.scrape("https://jobs.lever.co/beta")

    assert len(postings) == 2
    assert postings[0].external_id == "a1b2c3d4-0000-1111-2222-333344445555"
    assert postings[0].location == "Remote (India)"
    assert postings[0].employment_type is EmploymentType.FULL_TIME
    assert postings[0].posted_at is not None
    assert postings[0].posted_at.date().isoformat() == "2025-08-01"


def test_ashby_parses():
    scraper = AshbyScraper(_client(_load("ashby.json")))
    postings = scraper.scrape("https://jobs.ashbyhq.com/gamma")

    assert len(postings) == 1
    assert postings[0].title == "Platform Engineer"
    assert postings[0].employment_type is EmploymentType.FULL_TIME


def test_workday_parses_and_builds_apply_url():
    scraper = WorkdayScraper(
        _client(_load("workday.json"), expect_url_contains="/wday/cxs/acme/Careers/jobs")
    )
    postings = scraper.scrape("https://acme.wd1.myworkdayjobs.com/en-US/Careers")

    assert [p.title for p in postings] == [
        "Senior Software Engineer, Backend",
        "Enterprise Account Executive",
    ]
    first = postings[0]
    assert first.source == "workday"
    assert first.external_id == "JR12345"
    assert first.location == "India, Karnataka, Bengaluru"
    assert first.apply_url == (
        "https://acme.wd1.myworkdayjobs.com/en-US/Careers"
        "/job/India-Bengaluru/Senior-Software-Engineer_JR12345"
    )


def test_workday_rejects_non_workday_url():
    with pytest.raises(ScraperError):
        WorkdayScraper(_client({})).scrape("https://boards.greenhouse.io/acme")


def test_smartrecruiters_parses():
    scraper = SmartRecruitersScraper(
        _client(_load("smartrecruiters.json"), expect_url_contains="/companies/Acme/postings")
    )
    postings = scraper.scrape("https://careers.smartrecruiters.com/Acme")

    assert len(postings) == 1
    assert postings[0].external_id == "743999900000001"
    assert postings[0].location == "Bengaluru, Karnataka, in"
    assert postings[0].employment_type is EmploymentType.FULL_TIME
    assert postings[0].apply_url == "https://jobs.smartrecruiters.com/Acme/743999900000001"


def test_amazon_parses_india_scoped_and_flags_interns():
    scraper = AmazonScraper(
        _client(_load("amazon.json"), expect_url_contains="normalized_country_code%5B%5D=IND")
    )
    postings = scraper.scrape("https://www.amazon.jobs")

    assert [p.title for p in postings] == [
        "Software Development Engineer, Payments",
        "Software Dev Engineer Intern",
    ]
    first = postings[0]
    assert first.source == "amazon"
    assert first.external_id == "10517816"
    assert first.location == "Bengaluru, Karnataka, IND"
    assert first.employment_type is EmploymentType.FULL_TIME
    assert first.apply_url == (
        "https://www.amazon.jobs/en/jobs/2700123/software-development-engineer-payments"
    )
    assert first.posted_at is not None and first.posted_at.year == 2026
    assert postings[1].employment_type is EmploymentType.INTERNSHIP


def test_netflix_parses():
    scraper = NetflixScraper(_client(_load("netflix.json"), expect_url_contains="location=India"))
    postings = scraper.scrape("https://explore.jobs.netflix.net")

    assert len(postings) == 1
    assert postings[0].external_id == "JR42140"
    assert postings[0].location == "Mumbai,India"
    assert postings[0].apply_url.endswith("/careers/job/790317836990")
    assert postings[0].posted_at is not None


def test_http_error_becomes_scraper_error():
    scraper = GreenhouseScraper(_client({"error": "not found"}, status=404))
    with pytest.raises(ScraperError):
        scraper.scrape("https://boards.greenhouse.io/missing")


def test_slug_extraction_requires_a_path():
    with pytest.raises(ScraperError):
        BaseScraper._slug_from_url("https://boards.greenhouse.io")


def test_registry_maps_parser_types():
    assert get_scraper_class(ParserType.GREENHOUSE) is GreenhouseScraper
    assert get_scraper_class(ParserType.LEVER) is LeverScraper
    assert get_scraper_class(ParserType.WORKDAY) is WorkdayScraper
    assert get_scraper_class(ParserType.SMARTRECRUITERS) is SmartRecruitersScraper
    assert get_scraper_class(ParserType.AMAZON) is AmazonScraper
    assert get_scraper_class(ParserType.NETFLIX) is NetflixScraper
    with pytest.raises(ScraperError):
        get_scraper_class(ParserType.CUSTOM)


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("Full-time", EmploymentType.FULL_TIME),
        ("FullTime", EmploymentType.FULL_TIME),
        ("intern", EmploymentType.INTERNSHIP),
        ("Contract", EmploymentType.CONTRACT),
        ("weird value", EmploymentType.OTHER),
        (None, None),
    ],
)
def test_normalize_employment_type(raw, expected):
    assert normalize_employment_type(raw) == expected
