import pytest
from pydantic import ValidationError

from app.models.enums import ParserType
from app.schemas.company import CompanyCreate
from app.schemas.keyword_rule import KeywordRuleCreate


def test_company_create_accepts_valid_payload():
    company = CompanyCreate(
        name="Acme",
        career_url="https://boards.greenhouse.io/acme",
        parser_type="greenhouse",
    )
    assert company.parser_type is ParserType.GREENHOUSE
    assert company.active is True


def test_company_create_rejects_bad_url():
    with pytest.raises(ValidationError):
        CompanyCreate(name="Acme", career_url="not-a-url", parser_type="greenhouse")


def test_company_create_rejects_unknown_parser():
    with pytest.raises(ValidationError):
        CompanyCreate(name="Acme", career_url="https://x.com", parser_type="taleo")


def test_keyword_rule_weight_bounds():
    with pytest.raises(ValidationError):
        KeywordRuleCreate(role="backend", keyword="django", weight=0)
