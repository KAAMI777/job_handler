import pytest

from app.models.enums import EmploymentType
from app.scrapers.types import JobPosting
from app.services.matcher import evaluate

RULES = {
    "backend": [("backend", 1), ("api engineer", 2)],
    "platform": [("platform engineer", 1), ("sre", 1)],
}


def _posting(**kw) -> JobPosting:
    base = {
        "source": "greenhouse",
        "title": "Senior Backend Engineer",
        "location": "Bengaluru, India",
        "employment_type": EmploymentType.FULL_TIME,
        "apply_url": "https://x.com/1",
    }
    return JobPosting(**{**base, **kw})


def test_relevant_backend_role_in_india():
    result = evaluate(_posting(), RULES)
    assert result.is_relevant
    assert result.matched_roles == ["backend"]
    assert result.score == 20
    assert result.country == "India"


def test_internship_is_not_relevant():
    result = evaluate(_posting(employment_type=EmploymentType.INTERNSHIP), RULES)
    assert not result.is_relevant
    assert result.score == 0


def test_non_india_is_not_relevant_but_country_detected():
    result = evaluate(_posting(location="New York, NY"), RULES)
    assert not result.is_relevant
    assert result.country != "India"


def test_part_time_is_not_relevant():
    assert not evaluate(_posting(employment_type=EmploymentType.PART_TIME), RULES).is_relevant


def test_missing_employment_type_is_allowed():
    assert evaluate(_posting(employment_type=None), RULES).is_relevant


def test_no_keyword_match_is_not_relevant():
    result = evaluate(_posting(title="Accountant II"), RULES)
    assert not result.is_relevant
    assert result.matched_roles == []


def test_score_is_capped_and_sums_weights():
    result = evaluate(_posting(title="Backend / API Engineer, Platform Engineer SRE"), RULES)
    assert result.matched_roles == ["backend", "platform"]
    # weights: backend(1) + api engineer(2) + platform engineer(1) + sre(1) = 5 -> 100
    assert result.score == 100


def test_remote_india_counts_as_india():
    result = evaluate(_posting(location="Remote - India"), RULES)
    assert result.is_relevant


@pytest.mark.parametrize("loc", ["Remote", "Remote - EMEA", None])
def test_unknown_or_non_india_remote_not_relevant(loc):
    assert not evaluate(_posting(location=loc), RULES).is_relevant
