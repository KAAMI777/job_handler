import logging

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.db.session import engine

logger = logging.getLogger(__name__)

router = APIRouter(tags=["health"])


@router.get("/health", response_model=None)
def health() -> dict[str, str] | JSONResponse:
    """Liveness probe that also verifies database connectivity.

    Returns 200 when the database answers, 503 otherwise. The response shape is
    stable in both cases so the frontend can render a status without special-casing
    HTTP errors.
    """
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except SQLAlchemyError:
        logger.exception("Health check failed: database unreachable")
        return JSONResponse(
            status_code=503,
            content={"status": "degraded", "database": "disconnected"},
        )

    return {"status": "ok", "database": "connected"}
