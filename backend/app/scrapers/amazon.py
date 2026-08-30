from datetime import datetime
from typing import Any

from app.scrapers.base import BaseScraper
from app.scrapers.normalize import normalize_employment_type
from app.scrapers.types import JobPosting

# Amazon posts tens of thousands of roles globally; we ask its search API for India
# only. The matcher still has the final say on relevance.
API = (
    "https://www.amazon.jobs/en/search.json"
    "?normalized_country_code%5B%5D=IND&sort=recent&result_limit={limit}&offset={offset}"
)
_PAGE_SIZE = 100
_MAX_JOBS = 10000


class AmazonScraper(BaseScraper):
    """amazon.jobs public search API (India-scoped). One company, no per-board slug."""

    source = "amazon"

    def board_slug(self, career_url: str) -> str:
        return "amazon"

    def scrape(self, career_url: str) -> list[JobPosting]:
        postings: list[JobPosting] = []
        offset = 0
        while offset < _MAX_JOBS:
            payload = self._get_json(API.format(limit=_PAGE_SIZE, offset=offset))
            batch = payload.get("jobs") or []
            if not batch:
                break
            postings.extend(self._to_posting(job) for job in batch)
            offset += _PAGE_SIZE
            if offset >= (payload.get("hits") or 0):
                break
        return postings

    def _to_posting(self, job: dict[str, Any]) -> JobPosting:
        employment = (
            "internship" if job.get("is_intern") else job.get("job_schedule_type")
        )
        return JobPosting(
            source=self.source,
            external_id=str(job.get("id_icims") or job["id"]),
            title=job.get("title", "").strip(),
            location=job.get("normalized_location") or job.get("location"),
            employment_type=normalize_employment_type(employment),
            apply_url=f"https://www.amazon.jobs{job.get('job_path', '')}",
            description=job.get("description_short") or job.get("description"),
            posted_at=_parse_date(job.get("posted_date")),
        )


def _parse_date(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.strptime(value, "%B %d, %Y")
    except ValueError:
        return None
