from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status

from app.db.session import DbSession
from app.schemas.company import CompanyCreate, CompanyRead, CompanyUpdate
from app.services import company_service
from app.services.company_service import CareerUrlExistsError

router = APIRouter(prefix="/companies", tags=["companies"])

_CONFLICT = "A company with this career_url already exists"


@router.get("", response_model=list[CompanyRead])
def list_companies(
    db: DbSession,
    active_only: Annotated[bool, Query()] = False,
) -> list[CompanyRead]:
    return company_service.list_companies(db, active_only=active_only)


@router.post("", response_model=CompanyRead, status_code=status.HTTP_201_CREATED)
def create_company(payload: CompanyCreate, db: DbSession) -> CompanyRead:
    try:
        return company_service.create_company(db, payload)
    except CareerUrlExistsError as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, _CONFLICT) from exc


@router.get("/{company_id}", response_model=CompanyRead)
def get_company(company_id: int, db: DbSession) -> CompanyRead:
    company = company_service.get_company(db, company_id)
    if company is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Company not found")
    return company


@router.patch("/{company_id}", response_model=CompanyRead)
def update_company(company_id: int, payload: CompanyUpdate, db: DbSession) -> CompanyRead:
    try:
        company = company_service.update_company(db, company_id, payload)
    except CareerUrlExistsError as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, _CONFLICT) from exc
    if company is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Company not found")
    return company


@router.post("/{company_id}/disable", response_model=CompanyRead)
def disable_company(company_id: int, db: DbSession) -> CompanyRead:
    company = company_service.set_active(db, company_id, active=False)
    if company is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Company not found")
    return company


@router.post("/{company_id}/enable", response_model=CompanyRead)
def enable_company(company_id: int, db: DbSession) -> CompanyRead:
    company = company_service.set_active(db, company_id, active=True)
    if company is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Company not found")
    return company
