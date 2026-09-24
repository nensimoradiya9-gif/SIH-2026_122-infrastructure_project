from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
from models.project import Project
from models.activity import Activity

router = APIRouter(
    prefix="/api/ai-matching",
    tags=["AI Matching"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/")
def get_ai_matching(db: Session = Depends(get_db)):

    projects = db.query(Project).all()
    activities = db.query(Activity).all()

    results = []

    for activity in activities:
        matches = []

        for project in projects:
            if activity.project_id == project.id:
                matches.append({
                    "project_id": project.id,
                    "project_name": project.name,
                    "match_reason": "Activity belongs to this project"
                })

        results.append({
            "activity_id": activity.id,
            "activity_title": activity.title,
            "matches": matches
        })

    return {
        "total_activities": len(activities),
        "results": results
    }