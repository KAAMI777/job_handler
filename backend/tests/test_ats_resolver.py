import httpx
import pytest

from app.models.enums import ParserType
from app.services.ats_resolver import resolve


def _client(html: str = "", *, redirect_to: str | None = None):
    def handler(request: httpx.Request) -> httpx.Response:
        if redirect_to and str(request.url) != redirect_to:
            return httpx.Response(302, headers={"Location": redirect_to})
        return httpx.Response(200, text=html)

    return httpx.Client(transport=httpx.MockTransport(handler), follow_redirects=True)


def test_direct_ats_url_needs_no_fetch():
    r = resolve("https://boards.greenhouse.io/figma")
    assert r is not None and r.parser_type is ParserType.GREENHOUSE
    assert r.career_url == "https://boards.greenhouse.io/figma"


def test_detects_greenhouse_embed_in_html_ignoring_bad_slug():
    html = '<script src="https://boards.greenhouse.io/embed/job_board?for=stripe"></script>'
    r = resolve("https://stripe.com/jobs", client=_client(html))
    assert r is not None and r.parser_type is ParserType.GREENHOUSE
    assert r.career_url == "https://boards.greenhouse.io/stripe"


def test_detects_ashby_from_markup():
    html = '<div data-board="https://jobs.ashbyhq.com/notion/careers"></div>'
    r = resolve("https://www.notion.so/careers", client=_client(html))
    assert r is not None and r.parser_type is ParserType.ASHBY
    assert r.career_url == "https://jobs.ashbyhq.com/notion"


def test_detects_workday_url():
    html = 'window.location="https://nvidia.wd5.myworkdayjobs.com/NVIDIAExternalCareerSite"'
    r = resolve("https://nvidia.com/careers", client=_client(html))
    assert r is not None and r.parser_type is ParserType.WORKDAY
    assert r.career_url == "https://nvidia.wd5.myworkdayjobs.com/NVIDIAExternalCareerSite"


def test_detects_amazon():
    r = resolve("https://www.amazon.jobs/en/teams/software-development")
    assert r is not None and r.parser_type is ParserType.AMAZON


def test_detects_microsoft():
    r = resolve("https://careers.microsoft.com/v2/global/en/home.html")
    assert r is not None and r.parser_type is ParserType.MICROSOFT


def test_detects_oracle_hcm_from_markup():
    html = (
        '<a href="https://jpmc.fa.oraclecloud.com/hcmUI/CandidateExperience/en/'
        'sites/CX_1001/requisitions">Search jobs</a>'
    )
    r = resolve("https://careers.jpmorgan.com", client=_client(html))
    assert r is not None and r.parser_type is ParserType.ORACLE
    assert r.career_url == (
        "https://jpmc.fa.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1001"
    )


def test_follows_redirect_to_ats():
    r = resolve(
        "https://careers.acme.com",
        client=_client(redirect_to="https://jobs.lever.co/acme"),
    )
    assert r is not None and r.parser_type is ParserType.LEVER
    assert r.career_url == "https://jobs.lever.co/acme"


@pytest.mark.parametrize("html", ["", "<html><body>fully client rendered</body></html>"])
def test_returns_none_when_undetectable(html):
    assert resolve("https://example.com/careers", client=_client(html)) is None
