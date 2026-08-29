"""Detect which ATS a company's careers page uses, from a URL.

Given something like ``https://www.figma.com/careers/`` this fetches the page and
looks for the fingerprint of a supported ATS (an embedded board link, an API call
in the markup, a redirect target). Returns the canonical ``career_url`` + parser
type, or ``None`` when it can't tell (the caller then asks the user to pick).
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass

import httpx

from app.models.enums import ParserType
from app.scrapers.base import USER_AGENT

logger = logging.getLogger(__name__)

_BAD_SLUGS = {
    "embed", "job_board", "job-board", "posting-api", "postings", "v0", "v1",
    "boards", "companies", "www", "en", "en-us", "careers", "search", "jobs",
}

# (parser_type, pattern with group 1 = slug, canonical URL template)
_SLUG_PATTERNS: list[tuple[ParserType, re.Pattern[str], str]] = [
    (
        ParserType.GREENHOUSE,
        re.compile(r"greenhouse\.io/(?:embed/job_board\?for=|v1/boards/)([a-z0-9_-]+)", re.I),
        "https://boards.greenhouse.io/{}",
    ),
    (
        ParserType.GREENHOUSE,
        re.compile(r"(?:job-)?boards\.greenhouse\.io/([a-z0-9_-]+)", re.I),
        "https://boards.greenhouse.io/{}",
    ),
    (
        ParserType.LEVER,
        re.compile(r"(?:jobs|api)\.lever\.co/(?:v0/postings/)?([a-z0-9_-]+)", re.I),
        "https://jobs.lever.co/{}",
    ),
    (
        ParserType.ASHBY,
        re.compile(
            r"(?:jobs\.ashbyhq\.com|api\.ashbyhq\.com/posting-api/job-board)/([a-z0-9_-]+)", re.I
        ),
        "https://jobs.ashbyhq.com/{}",
    ),
    (
        ParserType.SMARTRECRUITERS,
        re.compile(
            r"(?:careers\.smartrecruiters\.com|api\.smartrecruiters\.com/v1/companies)/"
            r"([A-Za-z0-9_-]+)",
            re.I,
        ),
        "https://careers.smartrecruiters.com/{}",
    ),
]

_WORKDAY = re.compile(
    r"https?://([a-z0-9-]+\.[a-z0-9]+\.myworkdayjobs\.com/(?:[a-z]{2}-[A-Z]{2}/)?[A-Za-z0-9_-]+)",
    re.I,
)
_AMAZON = re.compile(r"amazon\.jobs", re.I)
_NETFLIX = re.compile(r"explore\.jobs\.netflix\.net|jobs\.netflix\.com", re.I)


@dataclass
class ResolvedAts:
    parser_type: ParserType
    career_url: str


def _match(text: str) -> ResolvedAts | None:
    if _AMAZON.search(text):
        return ResolvedAts(ParserType.AMAZON, "https://www.amazon.jobs")
    if _NETFLIX.search(text):
        return ResolvedAts(ParserType.NETFLIX, "https://explore.jobs.netflix.net")

    workday = _WORKDAY.search(text)
    if workday:
        return ResolvedAts(ParserType.WORKDAY, f"https://{workday.group(1)}")

    for parser_type, pattern, template in _SLUG_PATTERNS:
        for m in pattern.finditer(text):
            slug = m.group(1)
            if slug.lower() not in _BAD_SLUGS:
                return ResolvedAts(parser_type, template.format(slug))
    return None


def resolve(url: str, *, client: httpx.Client | None = None) -> ResolvedAts | None:
    """Best-effort ATS detection for ``url``. Never raises."""
    # The URL itself may already point at a known ATS.
    direct = _match(url)
    if direct is not None:
        return direct

    owns = client is None
    client = client or httpx.Client(
        timeout=15.0, headers={"User-Agent": USER_AGENT}, follow_redirects=True
    )
    try:
        response = client.get(url)
        # A redirect may have landed us on the ATS.
        landed = _match(str(response.url))
        if landed is not None:
            return landed
        return _match(response.text)
    except httpx.HTTPError as exc:
        logger.info("ATS resolve failed for %s: %s", url, exc)
        return None
    finally:
        if owns:
            client.close()
