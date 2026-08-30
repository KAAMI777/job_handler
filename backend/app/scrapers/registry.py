from app.models.enums import ParserType
from app.scrapers.amazon import AmazonScraper
from app.scrapers.ashby import AshbyScraper
from app.scrapers.base import BaseScraper, ScraperError
from app.scrapers.greenhouse import GreenhouseScraper
from app.scrapers.jsonld import JsonLdScraper
from app.scrapers.lever import LeverScraper
from app.scrapers.microsoft import MicrosoftScraper
from app.scrapers.netflix import NetflixScraper
from app.scrapers.oracle import OracleScraper
from app.scrapers.smartrecruiters import SmartRecruitersScraper
from app.scrapers.workday import WorkdayScraper

_REGISTRY: dict[ParserType, type[BaseScraper]] = {
    ParserType.GREENHOUSE: GreenhouseScraper,
    ParserType.LEVER: LeverScraper,
    ParserType.ASHBY: AshbyScraper,
    ParserType.WORKDAY: WorkdayScraper,
    ParserType.SMARTRECRUITERS: SmartRecruitersScraper,
    ParserType.ORACLE: OracleScraper,
    ParserType.AMAZON: AmazonScraper,
    ParserType.NETFLIX: NetflixScraper,
    ParserType.MICROSOFT: MicrosoftScraper,
    ParserType.CUSTOM: JsonLdScraper,
}


def get_scraper_class(parser_type: ParserType) -> type[BaseScraper]:
    """Return the scraper class registered for ``parser_type``."""
    try:
        return _REGISTRY[parser_type]
    except KeyError as exc:
        raise ScraperError(f"no scraper implemented for parser_type={parser_type!r}") from exc


def supported_parser_types() -> set[ParserType]:
    return set(_REGISTRY)
