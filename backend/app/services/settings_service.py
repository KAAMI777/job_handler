"""Notification settings.

Two layers:

* ``app_settings`` — a single global row (legacy ``notify_email`` + default minimum
  score), merged over the environment. Used when auth is disabled.
* ``user_settings`` — one row per signed-in user, created on first read. Each row is an
  independent digest recipient.
"""

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.app_settings import SETTINGS_ROW_ID, AppSettings
from app.models.user_settings import UserSettings
from app.schemas.settings import SettingsRead, SettingsUpdate


@dataclass(frozen=True)
class Recipient:
    email: str
    min_score: int


def _app_row(db: Session) -> AppSettings:
    row = db.get(AppSettings, SETTINGS_ROW_ID)
    if row is None:
        row = AppSettings(id=SETTINGS_ROW_ID)
        db.add(row)
        db.commit()
        db.refresh(row)
    return row


def _global_min_score(db: Session) -> int:
    row = _app_row(db)
    if row.notify_min_score is not None:
        return row.notify_min_score
    return get_settings().notify_min_score


def _global_settings(db: Session) -> SettingsRead:
    env = get_settings()
    row = _app_row(db)
    email = row.notify_email if row.notify_email is not None else env.notify_email
    return SettingsRead(
        notify_min_score=_global_min_score(db),
        notify_email=email,
        notify_enabled=bool(email),
    )


def _user_row(db: Session, user: dict) -> UserSettings:
    row = db.get(UserSettings, user["id"])
    if row is None:
        row = UserSettings(user_id=user["id"], email=user["email"])
        db.add(row)
        db.commit()
        db.refresh(row)
    elif row.email != user["email"]:  # keep the address in sync with the account
        row.email = user["email"]
        db.commit()
        db.refresh(row)
    return row


def _is_real_user(user: dict) -> bool:
    return bool(user.get("email"))


def for_user(db: Session, user: dict) -> SettingsRead:
    """Effective settings for the caller, creating their row on first access."""
    if not _is_real_user(user):
        return _global_settings(db)
    row = _user_row(db, user)
    return SettingsRead(
        notify_min_score=(
            row.notify_min_score if row.notify_min_score is not None else _global_min_score(db)
        ),
        notify_email=row.email,
        notify_enabled=row.notify_enabled,
    )


def update_for_user(db: Session, user: dict, data: SettingsUpdate) -> SettingsRead:
    changes = data.model_dump(exclude_unset=True)

    if not _is_real_user(user):
        row = _app_row(db)
        for key in ("notify_min_score", "notify_email"):
            if key in changes:
                setattr(row, key, changes[key])
        db.commit()
        return _global_settings(db)

    row = _user_row(db, user)
    if "notify_enabled" in changes:
        row.notify_enabled = changes["notify_enabled"]
    if "notify_min_score" in changes:
        row.notify_min_score = changes["notify_min_score"]
    db.commit()
    return for_user(db, user)


def digest_recipients(db: Session) -> list[Recipient]:
    """Every distinct address that should receive the post-scrape digest."""
    global_min = _global_min_score(db)
    seen: set[str] = set()
    out: list[Recipient] = []

    for row in db.execute(
        select(UserSettings).where(UserSettings.notify_enabled.is_(True))
    ).scalars():
        key = row.email.strip().lower()
        if not key or key in seen:
            continue
        seen.add(key)
        out.append(
            Recipient(
                email=row.email.strip(),
                min_score=row.notify_min_score if row.notify_min_score is not None else global_min,
            )
        )

    # Legacy / auth-disabled global recipient(s).
    global_email = _global_settings(db).notify_email
    for addr in (e.strip() for e in (global_email or "").split(",")):
        if addr and addr.lower() not in seen:
            seen.add(addr.lower())
            out.append(Recipient(email=addr, min_score=global_min))

    return out
