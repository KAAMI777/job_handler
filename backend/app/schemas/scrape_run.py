from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import RunStatus, RunType


class ScrapeRunRequest(BaseModel):
    run_type: RunType = RunType.SCHEDULED


class ScrapeRunAccepted(BaseModel):
    """202 response from POST /api/v1/scrape/run — poll the run for results."""

    run_id: int
    status: RunStatus


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
