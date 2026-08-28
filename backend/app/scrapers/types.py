from datetime import datetime

from pydantic import BaseModel


class JobPosting(BaseModel):
    """Normalized output of every scraper.

    Scrapers are responsible only for producing these; matching, scoring and
    persistence happen downstream (Phase 5). No field here is scored or filtered.
    """

    source: str
    external_id: str | None = None
    title: str
    location: str | None = None
    employment_type: str | None = None
    apply_url: str
    description: str | None = None
    posted_at: datetime | None = None
