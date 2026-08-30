"""Generic scraper: read schema.org ``JobPosting`` data embedded in a careers page.

Many sites emit ``<script type="application/ld+json">`` blocks for Google-for-Jobs.
This adapter needs no per-company code — it just parses whatever the page ships.
It only sees jobs the page itself lists in JSON-LD (often a subset), so it is a
best-effort fallback, not a replacement for a real ATS adapter.
"""

import json
import re

from app.scrapers.base import BaseScraper, ScraperError
from app.scrapers.normalize import normalize_employment_type
from app.scrapers.types import JobPosting

_SCRIPT = re.compile(
    r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
    re.IGNORECASE | re.DOTALL,
)


class JsonLdScraper(BaseScraper):
    """``parser_type = custom`` — extract JobPosting JSON-LD from the page at career_url."""

    source = "jsonld"

    def board_slug(self, career_url: str) -> str:
        return career_url

    def scrape(self, career_url: str) -> list[JobPosting]:
        html = self._get_text(career_url)
        postings = [
            self._to_posting(node, career_url)
            for node in _iter_job_postings(html)
        ]
        if not postings:
            raise ScraperError(
                f"no schema.org JobPosting data found at {career_url} — use a specific parser_type"
            )
        return postings

    def _to_posting(self, node: dict, page_url: str) -> JobPosting:
        return JobPosting(
            source=self.source,
            external_id=str(node.get("identifier", {}).get("value") or node.get("@id") or "")
            or None,
            title=str(node.get("title", "")).strip(),
            location=_location(node),
            employment_type=normalize_employment_type(_first(node.get("employmentType"))),
            apply_url=str(node.get("url") or node.get("@id") or page_url),
            description=_strip_html(node.get("description")),
            posted_at=node.get("datePosted"),
        )


def _iter_job_postings(html: str):
    for block in _SCRIPT.findall(html):
        try:
            data = json.loads(block.strip())
        except ValueError:
            continue
        for node in _flatten(data):
            if isinstance(node, dict) and _is_job_posting(node.get("@type")):
                yield node


def _flatten(data):
    if isinstance(data, list):
        for item in data:
            yield from _flatten(item)
    elif isinstance(data, dict):
        if "@graph" in data:
            yield from _flatten(data["@graph"])
        else:
            yield data


def _is_job_posting(type_value) -> bool:
    if isinstance(type_value, list):
        return any(t == "JobPosting" for t in type_value)
    return type_value == "JobPosting"


def _first(value):
    if isinstance(value, list):
        return value[0] if value else None
    return value


def _location(node) -> str | None:
    loc = _first(node.get("jobLocation"))
    if not isinstance(loc, dict):
        return None
    addr = loc.get("address")
    if not isinstance(addr, dict):
        return None
    parts = [addr.get("addressLocality"), addr.get("addressRegion"), addr.get("addressCountry")]
    return ", ".join(p for p in parts if isinstance(p, str)) or None


def _strip_html(value) -> str | None:
    if not isinstance(value, str):
        return None
    return re.sub(r"<[^>]+>", " ", value)
