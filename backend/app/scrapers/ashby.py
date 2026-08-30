from typing import Any

from app.scrapers.base import BaseScraper
from app.scrapers.normalize import normalize_employment_type
from app.scrapers.types import JobPosting

API = "https://api.ashbyhq.com/posting-api/job-board/{slug}"


class AshbyScraper(BaseScraper):
    """Ashby job board (https://api.ashbyhq.com/posting-api/job-board)."""

    source = "ashby"

    def board_slug(self, career_url: str) -> str:
        return self._slug_from_url(career_url)

    def scrape(self, career_url: str) -> list[JobPosting]:
        slug = self.board_slug(career_url)
        payload = self._get_json(API.format(slug=slug))
        return [self._to_posting(job) for job in payload.get("jobs", [])]

    def _to_posting(self, job: dict[str, Any]) -> JobPosting:
        return JobPosting(
            source=self.source,
            external_id=str(job["id"]),
            title=job.get("title", "").strip(),
            location=job.get("location"),
            employment_type=normalize_employment_type(job.get("employmentType")),
            apply_url=job.get("jobUrl") or job.get("applyUrl", ""),
            description=job.get("descriptionPlain") or job.get("descriptionHtml"),
            posted_at=job.get("publishedAt") or job.get("updatedAt"),
        )
