"""Email digest of newly found relevant jobs, sent after a scrape run.

Opt-in: does nothing unless ``RESEND_API_KEY`` is set and there is at least one recipient
(a signed-in user with digests enabled, or the legacy global ``NOTIFY_EMAIL``). Each
recipient gets their own email, filtered by their own minimum score. A send failure is
logged, never raised — it must not fail the scrape run.
"""

from __future__ import annotations

import logging
from html import escape

import httpx
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.models.company import Company
from app.models.job import Job
from app.models.scrape_run import ScrapeRun
from app.services import settings_service

logger = logging.getLogger(__name__)

RESEND_ENDPOINT = "https://api.resend.com/emails"
_EMAIL_DESC_LEN = 280


def new_relevant_jobs(db: Session, run: ScrapeRun, min_score: int) -> list[tuple[str, Job]]:
    """(company_name, job) for relevant jobs first seen during this run at/above ``min_score``."""
    stmt = (
        select(Company.name, Job)
        .join(Company, Company.id == Job.company_id)
        .where(
            Job.is_relevant.is_(True),
            Job.score >= min_score,
            Job.first_seen_at >= run.started_at,
        )
        .order_by(Company.name, Job.score.desc(), Job.title)
    )
    return [(name, job) for name, job in db.execute(stmt)]


def send_new_jobs_digest(db: Session, run: ScrapeRun) -> bool:
    """Send each recipient their digest for ``run``. Returns True if any email was sent."""
    env = get_settings()
    if not env.resend_api_key:
        logger.debug("Email digest skipped: RESEND_API_KEY not set")
        return False

    recipients = settings_service.digest_recipients(db)
    if not recipients:
        logger.debug("Email digest skipped: no recipients")
        return False

    sent = 0
    for recipient in recipients:
        rows = new_relevant_jobs(db, run, recipient.min_score)
        if not rows:
            continue
        if _send_one(env, recipient.email, rows, run):
            sent += 1

    if not sent:
        logger.info("Email digest: nothing to send for run %s", run.id)
    return sent > 0


def _send_one(env: Settings, to: str, rows: list[tuple[str, Job]], run: ScrapeRun) -> bool:
    by_company: dict[str, list[Job]] = {}
    for name, job in rows:
        by_company.setdefault(name, []).append(job)

    payload = {
        "from": env.notify_from_email,
        "to": [to],
        "subject": f"{len(rows)} new software job(s) — Job Agent",
        "text": _text_body(by_company),
        "html": _html_body(by_company),
    }

    try:
        response = httpx.post(
            RESEND_ENDPOINT,
            headers={"Authorization": f"Bearer {env.resend_api_key}"},
            json=payload,
            timeout=15.0,
        )
    except httpx.HTTPError as exc:
        logger.warning("Email digest request failed for %s: %s", to, exc)
        return False

    if response.status_code >= 400:
        # Resend's body carries the real reason (bad key, unverified recipient, ...).
        logger.warning(
            "Email digest rejected by Resend for %s (%s): %s",
            to,
            response.status_code,
            response.text[:500],
        )
        return False

    logger.info("Email digest sent to %s for run %s (%s jobs)", to, run.id, len(rows))
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
