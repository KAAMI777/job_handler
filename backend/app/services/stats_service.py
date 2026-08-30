from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.company import Company
from app.models.job import Job
from app.schemas.stats import HIGH_SCORE_THRESHOLD, DashboardStats


def _count(db: Session, model, *conditions) -> int:
    return db.scalar(select(func.count()).select_from(model).where(*conditions)) or 0


def dashboard_stats(db: Session) -> DashboardStats:
    """Aggregate the numbers shown on the dashboard cards."""
    now = datetime.now(UTC)
    last_24h = now - timedelta(hours=24)
    last_7d = now - timedelta(days=7)

    return DashboardStats(
        total_companies=_count(db, Company),
        active_companies=_count(db, Company, Company.active.is_(True)),
        total_relevant_jobs=_count(
            db, Job, Job.is_relevant.is_(True), Job.is_active.is_(True)
        ),
        jobs_today=_count(db, Job, Job.created_at >= last_24h),
        new_relevant_jobs_today=_count(
            db, Job, Job.created_at >= last_24h, Job.is_relevant.is_(True)
        ),
        jobs_this_week=_count(
            db, Job, Job.first_seen_at >= last_7d, Job.is_relevant.is_(True)
        ),
        high_score_jobs=_count(
            db,
            Job,
            Job.is_relevant.is_(True),
            Job.is_active.is_(True),
            Job.score >= HIGH_SCORE_THRESHOLD,
        ),
    )
