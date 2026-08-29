from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.company import Company
from app.models.job import Job
from app.schemas.stats import DashboardStats


def dashboard_stats(db: Session) -> DashboardStats:
    """Aggregate the numbers shown on the dashboard cards."""
    since = datetime.now(UTC) - timedelta(hours=24)

    total_companies = db.scalar(select(func.count()).select_from(Company)) or 0
    active_companies = (
        db.scalar(select(func.count()).select_from(Company).where(Company.active.is_(True))) or 0
    )
    total_relevant_jobs = (
        db.scalar(
            select(func.count())
            .select_from(Job)
            .where(Job.is_relevant.is_(True), Job.is_active.is_(True))
        )
        or 0
    )
    jobs_today = (
        db.scalar(select(func.count()).select_from(Job).where(Job.created_at >= since)) or 0
    )
    new_relevant_jobs_today = (
        db.scalar(
            select(func.count())
            .select_from(Job)
            .where(Job.created_at >= since, Job.is_relevant.is_(True))
        )
        or 0
    )

    return DashboardStats(
        total_companies=total_companies,
        active_companies=active_companies,
        total_relevant_jobs=total_relevant_jobs,
        jobs_today=jobs_today,
        new_relevant_jobs_today=new_relevant_jobs_today,
    )
