from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any, ClassVar

import httpx
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_exponential

from app.scrapers.types import JobPosting

logger = logging.getLogger(__name__)

USER_AGENT = "JobAgentBot/1.0 (+https://job-handler.vercel.app)"
DEFAULT_TIMEOUT = 15.0


class ScraperError(Exception):
    """A scraper could not retrieve or parse a company's postings."""


def _is_transient(exc: BaseException) -> bool:
    """Retry network errors and 5xx responses, but not 4xx (they won't fix themselves)."""
    if isinstance(exc, httpx.TransportError):
        return True
    if isinstance(exc, httpx.HTTPStatusError):
        return exc.response.status_code >= 500
    return False


class BaseScraper(ABC):
    """Common HTTP plumbing for ATS scrapers.

    Subclasses implement :meth:`board_slug` (career URL -> board identifier) and
    :meth:`scrape` (the identifier -> normalized postings). No matching, scoring or
    filtering happens here.
    """

    source: ClassVar[str]

    def __init__(self, client: httpx.Client | None = None, *, retries: int = 2) -> None:
        self._retries = retries
        self._owns_client = client is None
        self._client = client or httpx.Client(
            timeout=DEFAULT_TIMEOUT,
            headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
            follow_redirects=True,
        )

    def __enter__(self) -> BaseScraper:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

    def close(self) -> None:
        if self._owns_client:
            self._client.close()

    def _get_json(self, url: str) -> Any:
        """GET ``url`` and return parsed JSON, retrying transient failures."""

        @retry(
            reraise=True,
            stop=stop_after_attempt(self._retries + 1),
            wait=wait_exponential(multiplier=0.5, max=8),
            retry=retry_if_exception(_is_transient),
        )
        def _do_request() -> Any:
            response = self._client.get(url)
            response.raise_for_status()
            return response.json()

        try:
            return _do_request()
        except (httpx.HTTPError, ValueError) as exc:
            raise ScraperError(f"{self.source}: request to {url} failed: {exc}") from exc

    @staticmethod
    def _slug_from_url(career_url: str) -> str:
        """Last non-empty path segment of a career URL (the common ATS pattern)."""
        path = httpx.URL(career_url).path.strip("/")
        if not path:
            raise ScraperError(f"cannot derive a board slug from {career_url!r}")
        return path.split("/")[-1]

    @abstractmethod
    def board_slug(self, career_url: str) -> str:
        """Extract the ATS board identifier from a company's career URL."""

    @abstractmethod
    def scrape(self, career_url: str) -> list[JobPosting]:
        """Return every posting currently listed for the company."""
