from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from database import SessionLocal
from models.settings import Settings
from models.user import User

router = APIRouter(
    prefix="/api/settings",
    tags=["Settings"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class SettingsRequest(BaseModel):
    user_id: int
    theme: Optional[str] = "light"
    notifications_enabled: Optional[bool] = True
    email_notifications: Optional[bool] = True


@router.post("/")
def create_settings(
    data: SettingsRequest,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(
        User.id == data.user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    existing_settings = db.query(Settings).filter(
        Settings.user_id == data.user_id
    ).first()

    if existing_settings:
        raise HTTPException(
            status_code=400,
            detail="Settings already exist for this user"
        )

    settings = Settings(
        user_id=data.user_id,
        theme=data.theme,
        notifications_enabled=data.notifications_enabled,
        email_notifications=data.email_notifications
    )

    db.add(settings)
    db.commit()
    db.refresh(settings)

    return settings


@router.get("/{user_id}")
def get_settings(
    user_id: int,
    db: Session = Depends(get_db)
):
    settings = db.query(Settings).filter(
        Settings.user_id == user_id
    ).first()

    if not settings:
        raise HTTPException(
            status_code=404,
            detail="Settings not found"
        )

    return settings


@router.put("/{user_id}")
def update_settings(
    user_id: int,
    data: SettingsRequest,
    db: Session = Depends(get_db)
):
    settings = db.query(Settings).filter(
        Settings.user_id == user_id
    ).first()

    if not settings:
        raise HTTPException(
            status_code=404,
            detail="Settings not found"
        )

    settings.theme = data.theme
    settings.notifications_enabled = data.notifications_enabled
    settings.email_notifications = data.email_notifications

    db.commit()
    db.refresh(settings)

    return settings