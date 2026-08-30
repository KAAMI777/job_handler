from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.api.v1 import (
    companies,
    jobs,
    keyword_rules,
    saved_jobs,
    scrape,
    settings,
    stats,
)

# Every /api/v1 route requires an authenticated caller. When AUTH_ENABLED is false
# (the default) get_current_user waves requests through as a local user, so this is a
# no-op until Supabase auth is switched on.
api_router = APIRouter(prefix="/api/v1", dependencies=[Depends(get_current_user)])
api_router.include_router(companies.router)
api_router.include_router(jobs.router)
api_router.include_router(keyword_rules.router)
api_router.include_router(saved_jobs.router)
api_router.include_router(scrape.router)
api_router.include_router(settings.router)
api_router.include_router(stats.router)
