# Import every model module so Alembic autogenerate and Base.metadata see them.
from app.models.app_settings import AppSettings
from app.models.company import Company
from app.models.job import Job
from app.models.keyword_rule import KeywordRule
from app.models.saved_job import SavedJob
from app.models.scrape_run import ScrapeRun

__all__ = ["AppSettings", "Company", "Job", "KeywordRule", "SavedJob", "ScrapeRun"]
