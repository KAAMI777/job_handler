"""CRUD for the matcher's keyword rules (role -> keyword -> weight).

Uniqueness of ``(role, keyword)`` is enforced here (friendly error) and by the DB
constraint (race safety), same pattern as ``company_service.career_url``.
"""

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.keyword_rule import KeywordRule
from app.schemas.keyword_rule import KeywordRuleCreate, KeywordRuleUpdate


class KeywordRuleExistsError(Exception):
    """Raised when a rule with the same (role, keyword) already exists."""


def list_rules(db: Session) -> list[KeywordRule]:
    stmt = select(KeywordRule).order_by(KeywordRule.role, KeywordRule.keyword)
    return list(db.scalars(stmt))


def create_rule(db: Session, data: KeywordRuleCreate) -> KeywordRule:
    rule = KeywordRule(**data.model_dump())
    db.add(rule)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise KeywordRuleExistsError(f"{data.role}/{data.keyword}") from exc
    db.refresh(rule)
    return rule


def update_rule(db: Session, rule_id: int, data: KeywordRuleUpdate) -> KeywordRule | None:
    rule = db.get(KeywordRule, rule_id)
    if rule is None:
        return None
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(rule, key, value)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise KeywordRuleExistsError(f"{rule.role}/{rule.keyword}") from exc
    db.refresh(rule)
    return rule


def delete_rule(db: Session, rule_id: int) -> bool:
    rule = db.get(KeywordRule, rule_id)
    if rule is None:
        return False
    db.delete(rule)
    db.commit()
    return True
