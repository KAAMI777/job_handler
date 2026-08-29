"""The user's personal job tracker (starred / applied). Single-user for now."""

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.enums import SavedStatus
from app.models.job import Job
from app.models.saved_job import SavedJob


def list_saved(db: Session, *, status: SavedStatus | None = None) -> list[SavedJob]:
    stmt = (
        select(SavedJob)
        .options(joinedload(SavedJob.job))
        .order_by(SavedJob.updated_at.desc())
    )
    if status is not None:
        stmt = stmt.where(SavedJob.status == status)
    return list(db.scalars(stmt))


def upsert(db: Session, job_id: int, status: SavedStatus) -> SavedJob | None:
    """Star a job or move it between saved/applied. Returns None if the job doesn't exist."""
    if db.get(Job, job_id) is None:
        return None

    saved = db.scalar(select(SavedJob).where(SavedJob.job_id == job_id))
    if saved is None:
        saved = SavedJob(job_id=job_id, status=status)
        db.add(saved)
    else:
        saved.status = status
    db.commit()
    db.refresh(saved)
    return saved


def remove(db: Session, job_id: int) -> bool:
    saved = db.scalar(select(SavedJob).where(SavedJob.job_id == job_id))
    if saved is None:
        return False
    db.delete(saved)
    db.commit()
    return True
