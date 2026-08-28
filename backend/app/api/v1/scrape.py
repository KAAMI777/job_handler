from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, HTTPException, Query, status

from app.db.session import DbSession
from app.schemas.scrape_run import ScrapeRunAccepted, ScrapeRunRead, ScrapeRunRequest
from app.services import scrape_service

router = APIRouter(prefix="/scrape", tags=["scrape"])


@router.post("/run", response_model=ScrapeRunAccepted, status_code=status.HTTP_202_ACCEPTED)
def start_scrape_run(
    payload: ScrapeRunRequest,
    background_tasks: BackgroundTasks,
    db: DbSession,
) -> ScrapeRunAccepted:
    """Kick off a scrape. Returns immediately; poll ``GET /scrape/run/{run_id}``.

    409 if a run is already in progress (its id is in the response detail).
    """
    scrape_service.reap_stale_runs(db)

    in_progress = scrape_service.active_run(db)
    if in_progress is not None:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            detail={"message": "A scrape run is already in progress", "run_id": in_progress.id},
        )

    run = scrape_service.create_run(db, payload.run_type)
    background_tasks.add_task(scrape_service.execute_run, run.id)
    return ScrapeRunAccepted(run_id=run.id, status=run.status)


@router.get("/run/{run_id}", response_model=ScrapeRunRead)
def get_scrape_run(run_id: int, db: DbSession) -> ScrapeRunRead:
    run = scrape_service.get_run(db, run_id)
    if run is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Scrape run not found")
    return run


@router.get("/runs", response_model=list[ScrapeRunRead])
def list_scrape_runs(
    db: DbSession,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> list[ScrapeRunRead]:
    return scrape_service.list_runs(db, limit=limit)
