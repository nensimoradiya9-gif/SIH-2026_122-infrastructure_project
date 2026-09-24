from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from database import SessionLocal
from models.activity_capture import ActivityCapture
from models.user import User

router = APIRouter(
    prefix="/api/activity-capture",
    tags=["Activity Capture"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class ActivityCaptureRequest(BaseModel):
    user_id: int
    action: str
    description: Optional[str] = None


@router.post("/")
def create_activity_capture(
    data: ActivityCaptureRequest,
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

    activity = ActivityCapture(
        user_id=data.user_id,
        action=data.action,
        description=data.description
    )

    db.add(activity)
    db.commit()
    db.refresh(activity)

    return activity


@router.get("/")
def get_activity_captures(
    db: Session = Depends(get_db)
):
    return (
        db.query(ActivityCapture)
        .order_by(ActivityCapture.created_at.desc())
        .all()
    )


@router.get("/user/{user_id}")
def get_user_activity(
    user_id: int,
    db: Session = Depends(get_db)
):
    return (
        db.query(ActivityCapture)
        .filter(ActivityCapture.user_id == user_id)
        .order_by(ActivityCapture.created_at.desc())
        .all()
    )