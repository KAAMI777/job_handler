from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import SavedStatus
from app.schemas.job import JobRead


class SavedJobUpsert(BaseModel):
    status: SavedStatus = SavedStatus.SAVED


class SavedJobRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    job_id: int
    status: SavedStatus
    created_at: datetime
    updated_at: datetime
    job: JobRead
