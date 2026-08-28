import logging
from logging.config import dictConfig

from app.core.config import get_settings


def configure_logging() -> None:
    """Configure root logging once, using the level from settings.

    Kept deliberately simple (plain text to stdout). Structured/JSON output can be
    added here later without touching call sites.
    """
    settings = get_settings()
    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "%(asctime)s %(levelname)-8s %(name)s: %(message)s",
                },
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                },
            },
            "root": {
                "handlers": ["console"],
                "level": settings.log_level.upper(),
            },
            "loggers": {
                "uvicorn.access": {"level": "INFO"},
            },
        }
    )
    logging.getLogger(__name__).debug("Logging configured (level=%s)", settings.log_level)
