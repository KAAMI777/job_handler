"""Turn a scraped :class:`JobPosting` into stored-job fields.

Rules (per project decisions):
- internships and anything not full-time are never relevant;
- only India / remote-in-India roles are relevant;
- a role must match at least one active keyword to be relevant;
- everything else is still stored, just with ``is_relevant = False``.

``score`` (0-100) only ranks the relevant set. It is deliberately simple and
explainable so the Settings-page keyword weights are predictable:
``score = min(100, 20 * sum(weight of each distinct keyword matched in the title))``.
"""

from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass, field

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.enums import EmploymentType
from app.models.keyword_rule import KeywordRule
from app.scrapers.types import JobPosting
from app.services.geo import detect_country

RuleMap = dict[str, list[tuple[str, int]]]  # role -> [(keyword, weight), ...]

_SCORE_PER_WEIGHT = 20


@dataclass
class MatchResult:
    is_relevant: bool
    score: int
    matched_roles: list[str] = field(default_factory=list)
    country: str | None = None


def load_rules(db: Session) -> RuleMap:
    """Read active keyword rules from the database into a role -> keywords map."""
    rules: RuleMap = defaultdict(list)
    stmt = select(KeywordRule).where(KeywordRule.is_active.is_(True))
    for rule in db.scalars(stmt):
        rules[rule.role].append((rule.keyword.lower(), rule.weight))
    return dict(rules)


def _keyword_hits(title: str, rules: RuleMap) -> tuple[list[str], int]:
    """Return matched role names and the summed weight of distinct matched keywords."""
    haystack = title.lower()
    matched_roles: list[str] = []
    weight_total = 0
    for role, keywords in rules.items():
        role_hit = False
        for keyword, weight in keywords:
            if re.search(rf"(?<!\w){re.escape(keyword)}(?!\w)", haystack):
                weight_total += weight
                role_hit = True
        if role_hit:
            matched_roles.append(role)
    return sorted(matched_roles), weight_total


def evaluate(posting: JobPosting, rules: RuleMap) -> MatchResult:
    country = detect_country(posting.location)
    matched_roles, weight_total = _keyword_hits(posting.title, rules)
    score = min(100, _SCORE_PER_WEIGHT * weight_total)

    disqualified = (
        posting.employment_type in (EmploymentType.INTERNSHIP, EmploymentType.PART_TIME)
        or (
            posting.employment_type is not None
            and posting.employment_type != EmploymentType.FULL_TIME
        )
        or country != "India"
        or not matched_roles
    )

    return MatchResult(
        is_relevant=not disqualified,
        score=score if not disqualified else 0,
        matched_roles=matched_roles,
        country=country,
    )
