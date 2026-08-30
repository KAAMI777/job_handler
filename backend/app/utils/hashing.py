import hashlib
import re

_WHITESPACE = re.compile(r"\s+")


def _normalize(value: str | None) -> str:
    """Lowercase, collapse whitespace, strip — so trivial formatting changes don't
    produce a different hash."""
    if not value:
        return ""
    return _WHITESPACE.sub(" ", value).strip().lower()


def job_hash(
    *,
    company_id: int,
    external_id: str | None,
    title: str,
    location: str | None,
    apply_url: str,
) -> str:
    """Deterministic dedup key for a job posting.

    Prefers the ATS's own id when available; otherwise derives one from the stable
    fields of the posting. Returns a hex SHA-256 digest.
    """
    if external_id:
        payload = f"{company_id}|{external_id.strip()}"
    else:
        payload = "|".join(
            [
                str(company_id),
                _normalize(title),
                _normalize(location),
                _normalize(apply_url),
            ]
        )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
