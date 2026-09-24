from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import date

from database import SessionLocal
from models.activity import Activity
from models.project import Project


router = APIRouter(
    prefix="/api/activities",
    tags=["Activities"]
)


# -----------------------------------------
# Database
# -----------------------------------------
def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


# -----------------------------------------
# Activity Request Schema
# -----------------------------------------
class ActivityRequest(BaseModel):

    project_id: int

    title: str

    description: Optional[str] = None

    # Planned Start
    activity_date: Optional[date] = None

    # Planned End
    planned_end: Optional[date] = None

    # Actual Start
    actual_start: Optional[date] = None

    status: Optional[str] = "pending"

    assigned_to: Optional[str] = None

    priority: Optional[str] = "medium"


# -----------------------------------------
# CREATE ACTIVITY
# -----------------------------------------
@router.post("/")
def create_activity(
    data: ActivityRequest,
    db: Session = Depends(get_db)
):

    # Check project
    project = (
        db.query(Project)
        .filter(Project.id == data.project_id)
        .first()
    )

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    activity = Activity(
        project_id=data.project_id,
        title=data.title,
        description=data.description,
        activity_date=data.activity_date,
        planned_end=data.planned_end,
        actual_start=data.actual_start,
        status=data.status,
        assigned_to=data.assigned_to,
        priority=data.priority
    )

    db.add(activity)

    db.commit()

    db.refresh(activity)

    return activity


# -----------------------------------------
# GET ALL ACTIVITIES
# -----------------------------------------
@router.get("/")
def get_activities(
    db: Session = Depends(get_db)
):

    return (
        db.query(Activity)
        .order_by(Activity.activity_date.asc())
        .all()
    )


# -----------------------------------------
# GET ONE ACTIVITY
# -----------------------------------------
@router.get("/{activity_id}")
def get_activity(
    activity_id: int,
    db: Session = Depends(get_db)
):

    activity = (
        db.query(Activity)
        .filter(Activity.id == activity_id)
        .first()
    )

    if not activity:
        raise HTTPException(
            status_code=404,
            detail="Activity not found"
        )

    return activity


# -----------------------------------------
# UPDATE ACTIVITY
# -----------------------------------------
@router.put("/{activity_id}")
def update_activity(
    activity_id: int,
    data: ActivityRequest,
    db: Session = Depends(get_db)
):

    activity = (
        db.query(Activity)
        .filter(Activity.id == activity_id)
        .first()
    )

    if not activity:
        raise HTTPException(
            status_code=404,
            detail="Activity not found"
        )


    # Check project
    project = (
        db.query(Project)
        .filter(Project.id == data.project_id)
        .first()
    )

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )


    # Update fields
    activity.project_id = data.project_id

    activity.title = data.title

    activity.description = data.description

    activity.activity_date = data.activity_date

    activity.planned_end = data.planned_end

    activity.actual_start = data.actual_start

    activity.status = data.status

    activity.assigned_to = data.assigned_to

    activity.priority = data.priority


    db.commit()

    db.refresh(activity)

    return activity


# -----------------------------------------
# DELETE ACTIVITY
# -----------------------------------------
@router.delete("/{activity_id}")
def delete_activity(
    activity_id: int,
    db: Session = Depends(get_db)
):

    activity = (
        db.query(Activity)
        .filter(Activity.id == activity_id)
        .first()
    )

    if not activity:
        raise HTTPException(
            status_code=404,
            detail="Activity not found"
        )


    db.delete(activity)

    db.commit()


    return {
        "message": "Activity deleted successfully"
    }