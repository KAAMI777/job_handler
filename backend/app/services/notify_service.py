"""Email digest of newly found relevant jobs, sent after a scrape run.

Opt-in: does nothing unless ``RESEND_API_KEY`` and ``NOTIFY_EMAIL`` are set. A send
failure is logged, never raised — it must not fail the scrape run.
"""

from __future__ import annotations

import logging
from html import escape

import httpx
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.company import Company
from app.models.job import Job
from app.models.scrape_run import ScrapeRun

logger = logging.getLogger(__name__)

RESEND_ENDPOINT = "https://api.resend.com/emails"
_EMAIL_DESC_LEN = 280


def new_relevant_jobs(db: Session, run: ScrapeRun) -> list[tuple[str, Job]]:
    """(company_name, job) for relevant jobs first seen during this run."""
    settings = get_settings()
    stmt = (
        select(Company.name, Job)
        .join(Company, Company.id == Job.company_id)
        .where(
            Job.is_relevant.is_(True),
            Job.score >= settings.notify_min_score,
            Job.first_seen_at >= run.started_at,
        )
        .order_by(Company.name, Job.score.desc(), Job.title)
    )
    return [(name, job) for name, job in db.execute(stmt)]


def send_new_jobs_digest(db: Session, run: ScrapeRun) -> bool:
    """Build and send the digest for ``run``. Returns True only if an email was sent."""
    settings = get_settings()
    if not settings.resend_api_key or not settings.notify_email:
        logger.debug("Email digest skipped: RESEND_API_KEY / NOTIFY_EMAIL not set")
        return False

    rows = new_relevant_jobs(db, run)
    if not rows:
        logger.info("Email digest skipped: no new relevant jobs in run %s", run.id)
        return False

    by_company: dict[str, list[Job]] = {}
    for name, job in rows:
        by_company.setdefault(name, []).append(job)

    subject = f"{len(rows)} new software job(s) — Job Agent"
    payload = {
        "from": settings.notify_from_email,
        "to": [e.strip() for e in settings.notify_email.split(",") if e.strip()],
        "subject": subject,
        "text": _text_body(by_company),
        "html": _html_body(by_company),
    }

    try:
        response = httpx.post(
            RESEND_ENDPOINT,
            headers={"Authorization": f"Bearer {settings.resend_api_key}"},
            json=payload,
            timeout=15.0,
        )
        response.raise_for_status()
    except httpx.HTTPError as exc:
        logger.warning("Email digest failed to send: %s", exc)
        return False

    logger.info("Email digest sent for run %s (%s jobs)", run.id, len(rows))
    return True


def _short(text: str | None) -> str:
    if not text:
        return ""
    return text if len(text) <= _EMAIL_DESC_LEN else text[:_EMAIL_DESC_LEN].rstrip() + "…"


def _text_body(by_company: dict[str, list[Job]]) -> str:
    lines = ["New relevant jobs from the latest scrape:", ""]
    for company, jobs in by_company.items():
        lines.append(f"{company} ({len(jobs)})")
        for job in jobs:
            tags = ", ".join(job.matched_roles) or "—"
            lines.append(f"  - {job.title}  [{tags}]  score {job.score}")
            if job.location:
                lines.append(f"    {job.location}")
            desc = _short(job.description)
            if desc:
                lines.append(f"    {desc}")
            lines.append(f"    Apply: {job.apply_url}")
        lines.append("")
    return "\n".join(lines)


def _html_body(by_company: dict[str, list[Job]]) -> str:
    parts = ["<h2>New relevant jobs from the latest scrape</h2>"]
    for company, jobs in by_company.items():
        parts.append(f"<h3>{escape(company)} ({len(jobs)})</h3><ul>")
        for job in jobs:
            tags = escape(", ".join(job.matched_roles) or "—")
            loc = f" — {escape(job.location)}" if job.location else ""
            desc = escape(_short(job.description))
            parts.append(
                f'<li><a href="{escape(job.apply_url)}"><strong>{escape(job.title)}</strong></a>'
                f" <em>[{tags}]</em> · score {job.score}{loc}"
                + (f"<br><span>{desc}</span>" if desc else "")
                + "</li>"
            )
        parts.append("</ul>")
    return "".join(parts)
