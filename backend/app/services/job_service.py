"""Persist scraped postings as ``jobs`` rows.

Dedup key is ``job_hash``; existing rows are updated in place (no history). Rows
that stop appearing in a company's feed are marked ``is_active = False`` rather
than deleted.
"""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from app.models.company import Company
from app.models.job import Job
from app.scrapers.types import JobPosting
from app.services.matcher import MatchResult
from app.utils.hashing import job_hash

# Fields refreshed from the live posting on every scrape.
_MUTABLE = ("title", "location", "country", "employment_type", "apply_url", "description")


def _now() -> datetime:
    return datetime.now(UTC)


def upsert_job(
    db: Session, company: Company, posting: JobPosting, match: MatchResult
) -> tuple[Job, bool]:
    """Insert or update the job for ``posting``. Returns ``(job, created)``."""
    digest = job_hash(
        company_id=company.id,
        external_id=posting.external_id,
        title=posting.title,
        location=posting.location,
        apply_url=posting.apply_url,
    )

    values = {
        "title": posting.title,
        "location": posting.location,
        "country": match.country,
        "employment_type": posting.employment_type,
        "apply_url": posting.apply_url,
        "description": posting.description,
    }

    job = db.scalar(select(Job).where(Job.job_hash == digest))
    now = _now()
    created = job is None

    if job is None:
        job = Job(
            job_hash=digest,
            company_id=company.id,
            source=posting.source,
            external_id=posting.external_id,
            first_seen_at=now,
            **values,
        )
        db.add(job)
    else:
        for key in _MUTABLE:
            setattr(job, key, values[key])

    job.is_active = True
    job.last_seen_at = now
    job.is_relevant = match.is_relevant
    job.score = match.score
    job.matched_roles = match.matched_roles
    job.scored_at = now

    db.flush()
    return job, created


def list_jobs(
    db: Session,
    *,
    company_id: int | None = None,
    min_score: int | None = None,
    role: str | None = None,
    is_relevant: bool | None = True,
    is_active: bool | None = True,
    first_seen_after: datetime | None = None,
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[Job], int]:
    """Return a page of jobs matching the filters, plus the total match count."""
    filters = []
    if company_id is not None:
        filters.append(Job.company_id == company_id)
    if min_score is not None:
        filters.append(Job.score >= min_score)
    if role is not None:
        filters.append(Job.matched_roles.contains([role]))
    if is_relevant is not None:
        filters.append(Job.is_relevant.is_(is_relevant))
    if is_active is not None:
        filters.append(Job.is_active.is_(is_active))
    if first_seen_after is not None:
        filters.append(Job.first_seen_at >= first_seen_after)

    total = db.scalar(select(func.count()).select_from(Job).where(*filters)) or 0
    stmt = (
        select(Job)
        .where(*filters)
        .order_by(Job.score.desc(), Job.last_seen_at.desc())
        .limit(limit)
        .offset(offset)
    )
    return list(db.scalars(stmt)), total


def deactivate_missing(db: Session, company_id: int, seen_hashes: set[str]) -> int:
    """Mark still-active jobs of a company that were not seen this run as inactive.

    Call only after a *successful* scrape. An empty ``seen_hashes`` means the company
    genuinely has no open postings, so every active job is deactivated. Returns the
    number of rows affected.
    """
    conditions = [Job.company_id == company_id, Job.is_active.is_(True)]
    if seen_hashes:
        conditions.append(Job.job_hash.not_in(seen_hashes))

    result = db.execute(update(Job).where(*conditions).values(is_active=False))
    return result.rowcount or 0
