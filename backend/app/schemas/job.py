from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import EmploymentType


class JobRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    company_id: int
    title: str
    location: str | None
    country: str | None
    employment_type: EmploymentType | None
    apply_url: str
    is_relevant: bool
    score: int
    matched_roles: list[str]
    is_active: bool
    first_seen_at: datetime
    last_seen_at: datetime
    created_at: datetime


class JobListParams(BaseModel):
    """Query parameters for the jobs list endpoint (Phase 7)."""

    company_id: int | None = None
    min_score: int | None = None
    role: str | None = None
    is_relevant: bool = True
    is_active: bool = True
    limit: int = 50
    offset: int = 0
