import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from .db import engine

logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://job-handler.vercel.app",
    ],
    allow_origin_regex=r"https://job-handler-.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
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
