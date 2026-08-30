from datetime import UTC, datetime
from typing import Any

from app.scrapers.base import BaseScraper
from app.scrapers.normalize import normalize_employment_type
from app.scrapers.types import JobPosting

API = "https://api.lever.co/v0/postings/{slug}?mode=json"


class LeverScraper(BaseScraper):
    """Lever job board (https://api.lever.co/v0/postings)."""

    source = "lever"

    def board_slug(self, career_url: str) -> str:
        return self._slug_from_url(career_url)

    def scrape(self, career_url: str) -> list[JobPosting]:
        slug = self.board_slug(career_url)
        payload = self._get_json(API.format(slug=slug))
        return [self._to_posting(job) for job in payload]

    def _to_posting(self, job: dict[str, Any]) -> JobPosting:
        categories = job.get("categories") or {}
        created_ms = job.get("createdAt")
        posted_at = (
            datetime.fromtimestamp(created_ms / 1000, tz=UTC)
            if isinstance(created_ms, int | float)
            else None
        )
        return JobPosting(
            source=self.source,
            external_id=str(job["id"]),
            title=job.get("text", "").strip(),
            location=categories.get("location"),
            employment_type=normalize_employment_type(categories.get("commitment")),
            apply_url=job.get("hostedUrl") or job.get("applyUrl", ""),
            description=job.get("descriptionPlain") or job.get("description"),
            posted_at=posted_at,
        )
