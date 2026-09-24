from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
from models.activity import Activity

router = APIRouter(
    prefix="/api/schedule",
    tags=["Schedule"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/")
def get_schedule(db: Session = Depends(get_db)):
    activities = (
        db.query(Activity)
        .order_by(Activity.activity_date.asc())
        .all()
    )

    return activities


@router.get("/{schedule_date}")
def get_schedule_by_date(
    schedule_date: str,
    db: Session = Depends(get_db)
):
    activities = (
        db.query(Activity)
        .filter(Activity.activity_date == schedule_date)
        .all()
    )

    return activities