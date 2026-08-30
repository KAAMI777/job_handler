import re

import httpx

from app.scrapers.base import BaseScraper, ScraperError
from app.scrapers.normalize import normalize_employment_type
from app.scrapers.types import JobPosting

_SITE = re.compile(r"/sites/([A-Za-z0-9_-]+)")
_PAGE_SIZE = 100
_MAX_JOBS = 20000

_FINDER = "findReqs;siteNumber={site},limit={limit},offset={offset},sortBy=POSTING_DATES_DESC"
_EXPAND = "requisitionList.workLocation,requisitionList.secondaryLocations"


class OracleScraper(BaseScraper):
    """Oracle Fusion / HCM recruiting sites (``*.fa.oraclecloud.com``).

    Used by many banks and enterprises (JPMorgan, Citi, ...). Career URL looks like
    ``https://<tenant>.fa.oraclecloud.com/hcmUI/CandidateExperience/en/sites/<site>/requisitions``.
    """

    source = "oracle"

    def board_slug(self, career_url: str) -> str:
        url = httpx.URL(career_url)
        if "oraclecloud.com" not in url.host:
            raise ScraperError(f"{career_url!r} is not an oraclecloud.com URL")
        m = _SITE.search(url.path)
        if not m:
            raise ScraperError(f"cannot find /sites/<site> in {career_url!r}")
        return f"{url.host}/{m.group(1)}"

    def scrape(self, career_url: str) -> list[JobPosting]:
        host, site = self.board_slug(career_url).split("/", 1)
        base = f"https://{host}/hcmRestApi/resources/latest/recruitingCEJobRequisitions"

        postings: list[JobPosting] = []
        total = None
        offset = 0
        while offset < _MAX_JOBS:
            finder = _FINDER.format(site=site, limit=_PAGE_SIZE, offset=offset)
            payload = self._get_json(f"{base}?onlyData=true&expand={_EXPAND}&finder={finder}")
            block = (payload.get("items") or [{}])[0]
            batch = block.get("requisitionList") or []
            if not batch:
                break
            postings.extend(self._to_posting(job, host, site) for job in batch)
            if total is None:
                total = block.get("TotalJobsCount") or 0
            offset += _PAGE_SIZE
            if offset >= total:
                break
        return postings

    def _to_posting(self, job: dict, host: str, site: str) -> JobPosting:
        commitment = job.get("JobType") or job.get("JobSchedule") or job.get("ContractType")
        return JobPosting(
            source=self.source,
            external_id=str(job["Id"]),
            title=(job.get("Title") or "").strip(),
            location=job.get("PrimaryLocation"),
            employment_type=normalize_employment_type(commitment),
            apply_url=(
                f"https://{host}/hcmUI/CandidateExperience/en/sites/{site}/job/{job['Id']}"
            ),
            description=job.get("ShortDescriptionStr"),
            posted_at=job.get("PostedDate"),
        )
