from pydantic import BaseModel


class DashboardStats(BaseModel):
    total_companies: int
    active_companies: int
    total_relevant_jobs: int
    jobs_today: int
    new_relevant_jobs_today: int
