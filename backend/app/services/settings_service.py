"""Effective app settings: the single ``app_settings`` row merged over env defaults."""

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.app_settings import SETTINGS_ROW_ID, AppSettings
from app.schemas.settings import SettingsRead, SettingsUpdate


def _row(db: Session) -> AppSettings:
    row = db.get(AppSettings, SETTINGS_ROW_ID)
    if row is None:
        row = AppSettings(id=SETTINGS_ROW_ID)
        db.add(row)
        db.commit()
        db.refresh(row)
    return row


def get_effective(db: Session) -> SettingsRead:
    env = get_settings()
    row = _row(db)
    return SettingsRead(
        notify_min_score=(
            row.notify_min_score if row.notify_min_score is not None else env.notify_min_score
        ),
        notify_email=row.notify_email if row.notify_email is not None else env.notify_email,
    )


def update(db: Session, data: SettingsUpdate) -> SettingsRead:
    row = _row(db)
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(row, key, value)
    db.commit()
    return get_effective(db)
