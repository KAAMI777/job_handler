from typing import Any

from app.scrapers.base import BaseScraper
from app.scrapers.normalize import normalize_employment_type
from app.scrapers.types import JobPosting

API = "https://boards-api.greenhouse.io/v1/boards/{slug}/jobs?content=true"


class GreenhouseScraper(BaseScraper):
    """Greenhouse job board (https://boards-api.greenhouse.io)."""

    source = "greenhouse"

    def board_slug(self, career_url: str) -> str:
        return self._slug_from_url(career_url)

    def scrape(self, career_url: str) -> list[JobPosting]:
        slug = self.board_slug(career_url)
        payload = self._get_json(API.format(slug=slug))
        return [self._to_posting(job) for job in payload.get("jobs", [])]

    def _to_posting(self, job: dict[str, Any]) -> JobPosting:
        metadata = {m.get("name", "").lower(): m.get("value") for m in job.get("metadata") or []}
        employment_raw = metadata.get("employment type") or metadata.get("employment_type")
        return JobPosting(
            source=self.source,
            external_id=str(job["id"]),
            title=job.get("title", "").strip(),
            location=(job.get("location") or {}).get("name"),
            employment_type=normalize_employment_type(employment_raw),
            apply_url=job.get("absolute_url", ""),
            description=job.get("content"),
            posted_at=job.get("updated_at") or job.get("first_published"),
        )
