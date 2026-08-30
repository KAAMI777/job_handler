from app.scrapers.base import BaseScraper
from app.scrapers.normalize import normalize_employment_type
from app.scrapers.types import JobPosting

# Microsoft's own careers search service. India-scoped for the same reason as Amazon.
API = (
    "https://gcsservices.careers.microsoft.com/search/api/v1/search"
    "?lc=India&pg={page}&pgSz={size}&o=Relevance&flt=true"
)
_PAGE_SIZE = 20  # this endpoint caps the page size
_MAX_PAGES = 200


class MicrosoftScraper(BaseScraper):
    """careers.microsoft.com search API (India-scoped). One employer, no per-board slug."""

    source = "microsoft"

    def board_slug(self, career_url: str) -> str:
        return "microsoft"

    def scrape(self, career_url: str) -> list[JobPosting]:
        postings: list[JobPosting] = []
        page = 1
        total = None
        while page <= _MAX_PAGES:
            payload = self._get_json(API.format(page=page, size=_PAGE_SIZE))
            result = (payload.get("operationResult") or {}).get("result") or {}
            batch = result.get("jobs") or []
            if not batch:
                break
            postings.extend(self._to_posting(job) for job in batch)
            if total is None:
                total = result.get("totalJobs") or 0
            page += 1
            if page * _PAGE_SIZE >= total:
                break
        return postings

    def _to_posting(self, job: dict) -> JobPosting:
        props = job.get("properties") or {}
        return JobPosting(
            source=self.source,
            external_id=str(job.get("jobId") or job.get("jobNumber")),
            title=(job.get("title") or "").strip(),
            location=props.get("primaryLocation") or props.get("locations", [None])[0],
            employment_type=normalize_employment_type(props.get("employmentType")),
            apply_url=f"https://jobs.careers.microsoft.com/global/en/job/{job.get('jobId')}",
            description=props.get("description") or job.get("summary"),
            posted_at=job.get("postingDate") or props.get("postedDate"),
        )
