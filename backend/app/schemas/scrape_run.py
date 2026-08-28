from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import RunStatus, RunType


class ScrapeRunRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    run_type: RunType
    status: RunStatus
    started_at: datetime
    finished_at: datetime | None
    companies_checked: int
    new_jobs: int
    failed: int
    duration_seconds: float | None


class ScrapeRunResult(BaseModel):
    """The Phase 6 POST /api/v1/scrape/run response payload."""

    run_id: int
    checked: int
    new_jobs: int
    failed: int
    duration: float
