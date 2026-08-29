from fastapi import APIRouter

from app.db.session import DbSession
from app.schemas.settings import SettingsRead, SettingsUpdate
from app.services import settings_service

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("", response_model=SettingsRead)
def get_settings(db: DbSession) -> SettingsRead:
    """Effective settings — DB overrides merged over environment defaults."""
    return settings_service.get_effective(db)


@router.patch("", response_model=SettingsRead)
def update_settings(payload: SettingsUpdate, db: DbSession) -> SettingsRead:
    return settings_service.update(db, payload)
