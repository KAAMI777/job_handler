from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status

from app.db.session import DbSession
from app.models.enums import SavedStatus
from app.schemas.saved_job import SavedJobRead, SavedJobUpsert
from app.services import saved_job_service

router = APIRouter(prefix="/saved-jobs", tags=["saved-jobs"])


@router.get("", response_model=list[SavedJobRead])
def list_saved_jobs(
    db: DbSession,
    status_: Annotated[SavedStatus | None, Query(alias="status")] = None,
) -> list[SavedJobRead]:
    return saved_job_service.list_saved(db, status=status_)


@router.put("/{job_id}", response_model=SavedJobRead)
def upsert_saved_job(job_id: int, payload: SavedJobUpsert, db: DbSession) -> SavedJobRead:
    saved = saved_job_service.upsert(db, job_id, payload.status)
    if saved is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Job not found")
    return saved


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_saved_job(job_id: int, db: DbSession) -> None:
    if not saved_job_service.remove(db, job_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Saved job not found")
