from typing import Any

from app.scrapers.base import BaseScraper
from app.scrapers.normalize import normalize_employment_type
from app.scrapers.types import JobPosting

API = "https://api.smartrecruiters.com/v1/companies/{slug}/postings"
_PAGE_SIZE = 100


class SmartRecruitersScraper(BaseScraper):
    """SmartRecruiters public postings API (``api.smartrecruiters.com``)."""

    source = "smartrecruiters"

    def board_slug(self, career_url: str) -> str:
        # careers.smartrecruiters.com/<Company>  or  <company>.smartrecruiters.com
        host_label = career_url.split("//", 1)[-1].split(".", 1)[0]
        if host_label not in ("careers", "www", "jobs"):
            return host_label
        return self._slug_from_url(career_url)

    def scrape(self, career_url: str) -> list[JobPosting]:
        slug = self.board_slug(career_url)
        url = API.format(slug=slug)

        postings: list[JobPosting] = []
        offset = 0
        while True:
            payload = self._get_json(f"{url}?limit={_PAGE_SIZE}&offset={offset}")
            content = payload.get("content") or []
            if not content:
                break
            postings.extend(self._to_posting(job, slug) for job in content)
            offset += _PAGE_SIZE
            if offset >= (payload.get("totalFound") or 0):
                break
        return postings

    def _to_posting(self, job: dict[str, Any], slug: str) -> JobPosting:
        location = job.get("location") or {}
        loc_parts = [location.get("city"), location.get("region"), location.get("country")]
        return JobPosting(
            source=self.source,
            external_id=str(job["id"]),
            title=job.get("name", "").strip(),
            location=", ".join(p for p in loc_parts if p) or None,
            employment_type=normalize_employment_type(
                (job.get("typeOfEmployment") or {}).get("label")
            ),
            apply_url=f"https://jobs.smartrecruiters.com/{slug}/{job['id']}",
            posted_at=job.get("releasedDate"),
        )
