from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import date

from database import SessionLocal
from models.project import Project


router = APIRouter(
    prefix="/api/projects",
    tags=["Projects"]
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


class ProjectRequest(BaseModel):
    name: str
    description: Optional[str] = None
    location: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[str] = "active"


# CREATE PROJECT
@router.post("/")
def create_project(
    data: ProjectRequest,
    db: Session = Depends(get_db)
):
    project = Project(
        name=data.name,
        description=data.description,
        location=data.location,
        start_date=data.start_date,
        end_date=data.end_date,
        status=data.status
    )

    db.add(project)
    db.commit()
    db.refresh(project)

    return project


# GET ALL PROJECTS
@router.get("/")
def get_projects(
    db: Session = Depends(get_db)
):
    return (
        db.query(Project)
        .order_by(Project.id.asc())
        .all()
    )


# GET ONE PROJECT
@router.get("/{project_id}")
def get_project(
    project_id: int,
    db: Session = Depends(get_db)
):
    project = (
        db.query(Project)
        .filter(Project.id == project_id)
        .first()
    )

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    return project


# UPDATE PROJECT
@router.put("/{project_id}")
def update_project(
    project_id: int,
    data: ProjectRequest,
    db: Session = Depends(get_db)
):
    project = (
        db.query(Project)
        .filter(Project.id == project_id)
        .first()
    )

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    project.name = data.name
    project.description = data.description
    project.location = data.location
    project.start_date = data.start_date
    project.end_date = data.end_date
    project.status = data.status

    db.commit()
    db.refresh(project)

    return project


# DELETE PROJECT
@router.delete("/{project_id}")
def delete_project(
    project_id: int,
    db: Session = Depends(get_db)
):
    project = (
        db.query(Project)
        .filter(Project.id == project_id)
        .first()
    )

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    db.delete(project)
    db.commit()

    return {
        "message": "Project deleted successfully"
    }