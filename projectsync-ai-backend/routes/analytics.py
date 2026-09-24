from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import SessionLocal
from models.project import Project
from models.activity import Activity
from models.daily_report import DailyReport

router = APIRouter(
    prefix="/api/analytics",
    tags=["Analytics"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/")
def get_analytics(db: Session = Depends(get_db)):

    total_projects = db.query(Project).count()
    total_activities = db.query(Activity).count()
    total_reports = db.query(DailyReport).count()

    pending = (
        db.query(Activity)
        .filter(Activity.status == "pending")
        .count()
    )

    completed = (
        db.query(Activity)
        .filter(Activity.status == "completed")
        .count()
    )

    high_priority = (
        db.query(Activity)
        .filter(Activity.priority == "high")
        .count()
    )

    medium_priority = (
        db.query(Activity)
        .filter(Activity.priority == "medium")
        .count()
    )

    low_priority = (
        db.query(Activity)
        .filter(Activity.priority == "low")
        .count()
    )

    return {
        "projects": {
            "total": total_projects
        },
        "activities": {
            "total": total_activities,
            "pending": pending,
            "completed": completed
        },
        "priority": {
            "high": high_priority,
            "medium": medium_priority,
            "low": low_priority
        },
        "daily_reports": {
            "total": total_reports
        }
    }