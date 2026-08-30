from app.scrapers.base import BaseScraper, ScraperError
from app.scrapers.registry import get_scraper_class, supported_parser_types
from app.scrapers.types import JobPosting

__all__ = [
    "BaseScraper",
    "JobPosting",
    "ScraperError",
    "get_scraper_class",
    "supported_parser_types",
]
