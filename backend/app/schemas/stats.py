from pydantic import BaseModel

HIGH_SCORE_THRESHOLD = 40


class DashboardStats(BaseModel):
    total_companies: int
    active_companies: int
    total_relevant_jobs: int
    jobs_today: int
    new_relevant_jobs_today: int
    jobs_this_week: int
    high_score_jobs: int
