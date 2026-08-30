from fastapi import APIRouter

from app.api.deps import CurrentUser
from app.db.session import DbSession
from app.schemas.settings import SettingsRead, SettingsUpdate
from app.services import settings_service

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("", response_model=SettingsRead)
def get_settings(db: DbSession, user: CurrentUser) -> SettingsRead:
    """The caller's effective notification settings (their row is created on first read)."""
    return settings_service.for_user(db, user)


@router.patch("", response_model=SettingsRead)
def update_settings(payload: SettingsUpdate, db: DbSession, user: CurrentUser) -> SettingsRead:
    return settings_service.update_for_user(db, user, payload)
