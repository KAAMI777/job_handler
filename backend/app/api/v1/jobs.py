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
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> JobList:
    items, total = job_service.list_jobs(
        db,
        company_id=company_id,
        min_score=min_score,
        role=role,
        is_relevant=is_relevant,
        is_active=is_active,
        limit=limit,
        offset=offset,
    )
    return JobList(items=items, total=total, limit=limit, offset=offset)
