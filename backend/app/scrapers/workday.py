import re
from typing import Any

import httpx

from app.scrapers.base import BaseScraper, ScraperError
from app.scrapers.types import JobPosting

_LOCALE = re.compile(r"^[a-z]{2}-[A-Z]{2}$")
_PAGE_SIZE = 20  # Workday's CXS endpoint caps limit at 20.
_MAX_JOBS = 5000  # safety valve


class WorkdayScraper(BaseScraper):
    """Workday-hosted career sites (``*.myworkdayjobs.com``).

    Career URL looks like ``https://<tenant>.<dc>.myworkdayjobs.com[/en-US]/<site>``.
    The postings live behind the undocumented CXS JSON endpoint
    ``/wday/cxs/<tenant>/<site>/jobs`` (POST, offset pagination).
    """

    source = "workday"

    def board_slug(self, career_url: str) -> str:
        url = httpx.URL(career_url)
        host = url.host
        if not host.endswith("myworkdayjobs.com"):
            raise ScraperError(f"{career_url!r} is not a myworkdayjobs.com URL")
        tenant = host.split(".")[0]
        segments = [s for s in url.path.strip("/").split("/") if s and not _LOCALE.match(s)]
        if not tenant or not segments:
            raise ScraperError(f"cannot derive tenant/site from {career_url!r}")
        return f"{tenant}/{segments[-1]}"

    def scrape(self, career_url: str) -> list[JobPosting]:
        url = httpx.URL(career_url)
        host = url.host
        tenant, site = self.board_slug(career_url).split("/", 1)
        api = f"https://{host}/wday/cxs/{tenant}/{site}/jobs"

        postings: list[JobPosting] = []
        total = None
        offset = 0
        while offset < _MAX_JOBS:
            payload = self._post_json(
                api,
                {"limit": _PAGE_SIZE, "offset": offset, "searchText": "", "appliedFacets": {}},
            )
            batch = payload.get("jobPostings") or []
            if not batch:
                break
            postings.extend(self._to_posting(job, host, site, career_url) for job in batch)
            offset += _PAGE_SIZE
            # Workday only reports ``total`` on the first page.
            if total is None:
                total = payload.get("total") or 0
            if len(postings) >= total:
                break
        return postings

    def _to_posting(self, job: dict[str, Any], host: str, site: str, career_url: str) -> JobPosting:
        external_path = job.get("externalPath", "")
        bullets = job.get("bulletFields") or []
        return JobPosting(
            source=self.source,
            external_id=bullets[0] if bullets else (external_path or None),
            title=job.get("title", "").strip(),
            location=job.get("locationsText"),
            employment_type=None,  # not present in the list response
            apply_url=(
                f"https://{host}/en-US/{site}{external_path}" if external_path else career_url
            ),
        )
