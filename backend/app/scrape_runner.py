"""Standalone scrape entry point for a Render Cron Job.

    python -m app.scrape_runner

Runs one full scrape to completion in this process (no web server involved), then
exits 0 on success / partial, 1 on failure or if it could not start.
"""

import sys

from app.core.logging import configure_logging
from app.models.enums import RunStatus
from app.services import scrape_service


def main() -> int:
    configure_logging()
    run = scrape_service.run_scrape_now()
    if run is None:
        return 1
    return 0 if run.status in (RunStatus.SUCCESS, RunStatus.PARTIAL) else 1


if __name__ == "__main__":
    sys.exit(main())
