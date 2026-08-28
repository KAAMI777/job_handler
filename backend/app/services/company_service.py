"""Business logic for company records.

Keeps SQLAlchemy usage out of the API layer. Uniqueness of ``career_url`` is
enforced both here (friendly error) and by a DB constraint (race safety).
"""

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.company import Company
from app.schemas.company import CompanyCreate, CompanyUpdate


class CareerUrlExistsError(Exception):
    """Raised when a company with the same career_url already exists."""


def list_companies(db: Session, *, active_only: bool = False) -> list[Company]:
    stmt = select(Company).order_by(Company.name)
    if active_only:
        stmt = stmt.where(Company.active.is_(True))
    return list(db.scalars(stmt))


def get_company(db: Session, company_id: int) -> Company | None:
    return db.get(Company, company_id)


def _career_url_taken(db: Session, career_url: str, *, exclude_id: int | None = None) -> bool:
    stmt = select(Company.id).where(Company.career_url == career_url)
    if exclude_id is not None:
        stmt = stmt.where(Company.id != exclude_id)
    return db.scalar(stmt) is not None


def create_company(db: Session, data: CompanyCreate) -> Company:
    career_url = str(data.career_url)
    if _career_url_taken(db, career_url):
        raise CareerUrlExistsError(career_url)

    company = Company(
        name=data.name,
        career_url=career_url,
        parser_type=data.parser_type,
        active=data.active,
    )
    db.add(company)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise CareerUrlExistsError(career_url) from exc
    db.refresh(company)
    return company


def update_company(db: Session, company_id: int, data: CompanyUpdate) -> Company | None:
    company = db.get(Company, company_id)
    if company is None:
        return None

    fields = data.model_dump(exclude_unset=True)
    if "career_url" in fields:
        fields["career_url"] = str(fields["career_url"])
        if _career_url_taken(db, fields["career_url"], exclude_id=company_id):
            raise CareerUrlExistsError(fields["career_url"])

    for key, value in fields.items():
        setattr(company, key, value)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise CareerUrlExistsError(str(fields.get("career_url", ""))) from exc
    db.refresh(company)
    return company


def set_active(db: Session, company_id: int, *, active: bool) -> Company | None:
    company = db.get(Company, company_id)
    if company is None:
        return None
    company.active = active
    db.commit()
    db.refresh(company)
    return company
