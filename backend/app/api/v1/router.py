from fastapi import APIRouter

from app.api.v1 import companies, jobs, scrape, stats

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(companies.router)
api_router.include_router(jobs.router)
api_router.include_router(scrape.router)
api_router.include_router(stats.router)
