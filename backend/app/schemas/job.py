from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import EmploymentType


class JobRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    company_id: int
    source: str | None
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


class JobList(BaseModel):
    items: list[JobRead]
    total: int
    limit: int
    offset: int
