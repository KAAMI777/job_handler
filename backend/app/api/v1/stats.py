from fastapi import APIRouter

from app.db.session import DbSession
from app.schemas.stats import DashboardStats
from app.services import stats_service

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("", response_model=DashboardStats)
def get_dashboard_stats(db: DbSession) -> DashboardStats:
    return stats_service.dashboard_stats(db)
