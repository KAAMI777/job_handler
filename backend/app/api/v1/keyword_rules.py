from fastapi import APIRouter, HTTPException, status

from app.db.session import DbSession
from app.schemas.keyword_rule import KeywordRuleCreate, KeywordRuleRead, KeywordRuleUpdate
from app.services import keyword_rule_service
from app.services.keyword_rule_service import KeywordRuleExistsError

router = APIRouter(prefix="/keyword-rules", tags=["keyword-rules"])

_CONFLICT = "A rule for this role/keyword already exists"


@router.get("", response_model=list[KeywordRuleRead])
def list_keyword_rules(db: DbSession) -> list[KeywordRuleRead]:
    return keyword_rule_service.list_rules(db)


@router.post("", response_model=KeywordRuleRead, status_code=status.HTTP_201_CREATED)
def create_keyword_rule(payload: KeywordRuleCreate, db: DbSession) -> KeywordRuleRead:
    try:
        return keyword_rule_service.create_rule(db, payload)
    except KeywordRuleExistsError as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, _CONFLICT) from exc


@router.patch("/{rule_id}", response_model=KeywordRuleRead)
def update_keyword_rule(
    rule_id: int, payload: KeywordRuleUpdate, db: DbSession
) -> KeywordRuleRead:
    try:
        rule = keyword_rule_service.update_rule(db, rule_id, payload)
    except KeywordRuleExistsError as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, _CONFLICT) from exc
    if rule is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Rule not found")
    return rule


@router.delete("/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_keyword_rule(rule_id: int, db: DbSession) -> None:
    if not keyword_rule_service.delete_rule(db, rule_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Rule not found")
