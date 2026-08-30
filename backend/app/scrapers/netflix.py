from datetime import UTC, datetime
from typing import Any

from app.scrapers.base import BaseScraper
from app.scrapers.types import JobPosting

# Netflix runs on Eightfold. India-scoped for the same reason as Amazon.
API = (
    "https://explore.jobs.netflix.net/api/apply/v2/jobs"
    "?domain=netflix.com&location=India&start={start}&num={num}"
)
_PAGE_SIZE = 100
_MAX_JOBS = 5000


class NetflixScraper(BaseScraper):
    """Netflix careers (Eightfold ``explore.jobs.netflix.net``), India-scoped."""

    source = "netflix"

    def board_slug(self, career_url: str) -> str:
        return "netflix"

    def scrape(self, career_url: str) -> list[JobPosting]:
        postings: list[JobPosting] = []
        start = 0
        while start < _MAX_JOBS:
            payload = self._get_json(API.format(start=start, num=_PAGE_SIZE))
            batch = payload.get("positions") or []
            if not batch:
                break
            postings.extend(self._to_posting(job) for job in batch)
            start += _PAGE_SIZE
            if start >= (payload.get("count") or 0):
                break
        return postings

    def _to_posting(self, job: dict[str, Any]) -> JobPosting:
        created = job.get("t_create")
        return JobPosting(
            source=self.source,
            external_id=str(job.get("display_job_id") or job.get("ats_job_id") or job["id"]),
            title=job.get("name", "").strip(),
            location=job.get("location"),
            employment_type=None,
            apply_url=job.get("canonicalPositionUrl", ""),
            description=job.get("job_description") or None,
            posted_at=(
                datetime.fromtimestamp(created, tz=UTC)
                if isinstance(created, int | float)
                else None
            ),
        )
