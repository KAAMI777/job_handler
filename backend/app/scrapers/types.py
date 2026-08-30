from datetime import datetime

from pydantic import BaseModel, field_validator

from app.models.enums import EmploymentType
from app.utils.text import clean_description


class JobPosting(BaseModel):
    """Normalized output of every scraper.

    Scrapers are responsible only for producing these; matching, scoring and
    persistence happen downstream (Phase 5). No field here is scored or filtered.
    """

    source: str
    external_id: str | None = None
    title: str
    location: str | None = None
    employment_type: EmploymentType | None = None
    apply_url: str
    description: str | None = None
    posted_at: datetime | None = None

    @field_validator("description", mode="after")
    @classmethod
    def _trim_description(cls, value: str | None) -> str | None:
        # Keep only a short plain-text preview (bounds DB rows and peak memory).
        return clean_description(value)
