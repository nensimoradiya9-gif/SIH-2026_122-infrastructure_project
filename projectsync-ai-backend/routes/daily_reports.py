from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import date
import os

from database import SessionLocal
from models.daily_report import DailyReport
from models.project import Project


router = APIRouter(
    prefix="/api/daily-reports",
    tags=["Daily Reports"]
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


class DailyReportRequest(BaseModel):
    project_id: int
    report_date: date
    title: str
    description: Optional[str] = None
    submitted_by: Optional[str] = None
    status: Optional[str] = "submitted"


# CREATE DAILY REPORT
@router.post("/")
def create_daily_report(
    data: DailyReportRequest,
    db: Session = Depends(get_db)
):
    project = db.query(Project).filter(
        Project.id == data.project_id
    ).first()

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    report = DailyReport(
        project_id=data.project_id,
        report_date=data.report_date,
        title=data.title,
        description=data.description,
        submitted_by=data.submitted_by,
        status=data.status
    )

    db.add(report)
    db.commit()
    db.refresh(report)

    return report


# GET ALL DAILY REPORTS
@router.get("/")
def get_daily_reports(
    db: Session = Depends(get_db)
):
    return db.query(DailyReport).all()


# GET ONE DAILY REPORT
@router.get("/{report_id}")
def get_daily_report(
    report_id: int,
    db: Session = Depends(get_db)
):
    report = db.query(DailyReport).filter(
        DailyReport.id == report_id
    ).first()

    if not report:
        raise HTTPException(
            status_code=404,
            detail="Daily report not found"
        )

    return report


# UPDATE DAILY REPORT
@router.put("/{report_id}")
def update_daily_report(
    report_id: int,
    data: DailyReportRequest,
    db: Session = Depends(get_db)
):
    report = db.query(DailyReport).filter(
        DailyReport.id == report_id
    ).first()

    if not report:
        raise HTTPException(
            status_code=404,
            detail="Daily report not found"
        )

    project = db.query(Project).filter(
        Project.id == data.project_id
    ).first()

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    report.project_id = data.project_id
    report.report_date = data.report_date
    report.title = data.title
    report.description = data.description
    report.submitted_by = data.submitted_by
    report.status = data.status

    db.commit()
    db.refresh(report)

    return report


# DELETE DAILY REPORT
@router.delete("/{report_id}")
def delete_daily_report(
    report_id: int,
    db: Session = Depends(get_db)
):
    report = db.query(DailyReport).filter(
        DailyReport.id == report_id
    ).first()

    if not report:
        raise HTTPException(
            status_code=404,
            detail="Daily report not found"
        )

    db.delete(report)
    db.commit()

    return {
        "message": "Daily report deleted successfully"
    }


# UPLOAD REPORT FILE
@router.post("/{report_id}/upload")
def upload_report_file(
    report_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    report = db.query(DailyReport).filter(
        DailyReport.id == report_id
    ).first()

    if not report:
        raise HTTPException(
            status_code=404,
            detail="Daily report not found"
        )

    upload_dir = "uploads/daily_reports"
    os.makedirs(upload_dir, exist_ok=True)

    file_path = os.path.join(
        upload_dir,
        file.filename
    )

    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())

    report.file_name = file.filename
    report.file_path = file_path

    db.commit()
    db.refresh(report)

    return {
        "message": "File uploaded successfully",
        "file_name": file.filename,
        "file_path": file_path,
        "report_id": report.id
    }