from fastapi import APIRouter

api_router = APIRouter(prefix="/api/v1")

# Resource routers are included here as they land:
#   from app.api.v1 import companies, jobs, scrape
#   api_router.include_router(companies.router)
