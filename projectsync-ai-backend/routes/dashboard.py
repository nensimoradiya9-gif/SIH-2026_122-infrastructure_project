from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import SessionLocal
from models.project import Project
from models.activity import Activity
from models.daily_report import DailyReport


router = APIRouter(
    prefix="/api/dashboard",
    tags=["Dashboard"]
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


# -----------------------------------------
# Dashboard Summary
# -----------------------------------------
@router.get("/")
def get_dashboard(
    db: Session = Depends(get_db)
):

    total_projects = db.query(Project).count()

    total_activities = db.query(Activity).count()

    total_reports = db.query(DailyReport).count()

    pending_activities = (
        db.query(Activity)
        .filter(Activity.status == "pending")
        .count()
    )

    completed_activities = (
        db.query(Activity)
        .filter(Activity.status == "completed")
        .count()
    )

    return {
        "total_projects": total_projects,
        "total_activities": total_activities,
        "total_reports": total_reports,
        "pending_activities": pending_activities,
        "completed_activities": completed_activities
    }


# -----------------------------------------
# Dashboard Progress Trend
# -----------------------------------------
@router.get("/progress/")
def get_progress(
    db: Session = Depends(get_db)
):
    """
    Returns cumulative activity progress
    grouped by activity date.
    """

    activities = (
        db.query(Activity)
        .filter(Activity.activity_date.isnot(None))
        .order_by(Activity.activity_date.asc())
        .all()
    )

    if not activities:
        return []

    total_activities = len(activities)

    dates = sorted(
        set(activity.activity_date for activity in activities)
    )

    result = []

    for current_date in dates:

        planned_count = sum(
            1
            for activity in activities
            if activity.activity_date <= current_date
        )

        completed_count = sum(
            1
            for activity in activities
            if activity.activity_date <= current_date
            and activity.status == "completed"
        )

        planned_percentage = round(
            (planned_count / total_activities) * 100,
            2
        )

        actual_percentage = round(
            (completed_count / total_activities) * 100,
            2
        )

        result.append({
            "date": current_date.isoformat(),
            "planned": planned_percentage,
            "actual": actual_percentage
        })

    return result