from datetime import UTC, datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Query

from app.db.session import DbSession
from app.schemas.job import JobList
from app.services import job_service

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("", response_model=JobList)
def list_jobs(
    db: DbSession,
    company_id: Annotated[int | None, Query()] = None,
    min_score: Annotated[int | None, Query(ge=0, le=100)] = None,
    role: Annotated[str | None, Query()] = None,
    is_relevant: Annotated[bool | None, Query()] = True,
    is_active: Annotated[bool | None, Query()] = True,
    within_hours: Annotated[
        int | None, Query(ge=1, le=8760, description="Only jobs first seen in the last N hours")
    ] = None,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> JobList:
    first_seen_after = (
        datetime.now(UTC) - timedelta(hours=within_hours) if within_hours else None
    )
    items, total = job_service.list_jobs(
        db,
        company_id=company_id,
        min_score=min_score,
        role=role,
        is_relevant=is_relevant,
        is_active=is_active,
        first_seen_after=first_seen_after,
        limit=limit,
        offset=offset,
    )
    return JobList(items=items, total=total, limit=limit, offset=offset)
