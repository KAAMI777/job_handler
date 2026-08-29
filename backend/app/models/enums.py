from enum import Enum, StrEnum

from sqlalchemy import Enum as SAEnum


def pg_enum(enum_cls: type[Enum], name: str) -> SAEnum:
    """Build a SQLAlchemy Enum that stores the member *values* (lowercase) in Postgres,
    not the member names, so raw SQL and dashboard queries read naturally."""
    return SAEnum(enum_cls, name=name, values_callable=lambda e: [m.value for m in e])


class ParserType(StrEnum):
    """How a company's career page is scraped. Matches a scraper class in app/scrapers/."""

    GREENHOUSE = "greenhouse"
    LEVER = "lever"
    ASHBY = "ashby"
    WORKDAY = "workday"
    SMARTRECRUITERS = "smartrecruiters"
    AMAZON = "amazon"
    NETFLIX = "netflix"
    CUSTOM = "custom"


class EmploymentType(StrEnum):
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    INTERNSHIP = "internship"
    OTHER = "other"


class RunType(StrEnum):
    SCHEDULED = "scheduled"
    MANUAL = "manual"


class RunStatus(StrEnum):
    RUNNING = "running"
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"
