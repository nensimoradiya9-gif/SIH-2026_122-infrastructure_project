from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime
from collections import defaultdict
import os
import csv
import tempfile

from database import SessionLocal
from models.project import Project
from models.activity import Activity
from models.daily_report import DailyReport


router = APIRouter(
    prefix="/api/reports",
    tags=["Reports"]
)


REPORT_DIR = "generated_reports"
os.makedirs(REPORT_DIR, exist_ok=True)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


# ---------------------------------------------------------
# EXISTING OVERALL REPORT
# ---------------------------------------------------------

@router.get("/")
def get_reports(
    db: Session = Depends(get_db)
):
    projects = db.query(Project).all()
    activities = db.query(Activity).all()
    daily_reports = db.query(DailyReport).all()

    return {
        "total_projects": len(projects),
        "total_activities": len(activities),
        "total_daily_reports": len(daily_reports),
        "projects": projects,
        "activities": activities,
        "daily_reports": daily_reports
    }


# ---------------------------------------------------------
# EXISTING PROJECT REPORT
# ---------------------------------------------------------

@router.get("/project/{project_id}")
def get_project_report(
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

    activities = (
        db.query(Activity)
        .filter(Activity.project_id == project_id)
        .all()
    )

    daily_reports = (
        db.query(DailyReport)
        .filter(DailyReport.project_id == project_id)
        .all()
    )

    return {
        "project": project,
        "activities": activities,
        "daily_reports": daily_reports
    }


# ---------------------------------------------------------
# OVERALL PROJECT PROGRESS
# ---------------------------------------------------------

@router.get("/overall")
def overall_project_progress(
    project_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Activity)

    if project_id is not None:
        query = query.filter(
            Activity.project_id == project_id
        )

    activities = query.all()

    total = len(activities)

    completed = sum(
        1
        for activity in activities
        if activity.status == "completed"
    )

    pending = sum(
        1
        for activity in activities
        if activity.status == "pending"
    )

    percentage = (
        round((completed / total) * 100, 2)
        if total > 0
        else 0
    )

    return {
        "total_activities": total,
        "completed_activities": completed,
        "pending_activities": pending,
        "completion_percentage": percentage
    }


# ---------------------------------------------------------
# DISCIPLINE WISE PROGRESS
# ---------------------------------------------------------
#
# The current Activity model does not contain a discipline
# column. Therefore activities are grouped as "Unspecified".
#
# This endpoint can later use Activity.discipline after
# that field is added to the model.
# ---------------------------------------------------------

@router.get("/discipline")
def discipline_wise_progress(
    project_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Activity)

    if project_id is not None:
        query = query.filter(
            Activity.project_id == project_id
        )

    activities = query.all()

    result = defaultdict(
        lambda: {
            "total": 0,
            "completed": 0,
            "pending": 0
        }
    )

    for activity in activities:

        discipline = "Unspecified"

        result[discipline]["total"] += 1

        if activity.status == "completed":
            result[discipline]["completed"] += 1

        if activity.status == "pending":
            result[discipline]["pending"] += 1

    output = []

    for discipline, values in result.items():

        total = values["total"]

        percentage = (
            round(
                (values["completed"] / total) * 100,
                2
            )
            if total > 0
            else 0
        )

        output.append({
            "discipline": discipline,
            "total": total,
            "completed": values["completed"],
            "pending": values["pending"],
            "completion_percentage": percentage
        })

    return output


# ---------------------------------------------------------
# DELAY ANALYSIS
# ---------------------------------------------------------

@router.get("/delay-analysis")
def delay_analysis(
    project_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Activity)

    if project_id is not None:
        query = query.filter(
            Activity.project_id == project_id
        )

    activities = query.all()

    today = date.today()

    delayed = []
    on_track = []

    for activity in activities:

        is_delayed = False

        if (
            activity.planned_end
            and activity.status != "completed"
            and activity.planned_end < today
        ):
            is_delayed = True

        item = {
            "activity_id": activity.id,
            "title": activity.title,
            "planned_end": (
                activity.planned_end.isoformat()
                if activity.planned_end
                else None
            ),
            "status": activity.status,
            "priority": activity.priority
        }

        if is_delayed:
            delayed.append(item)
        else:
            on_track.append(item)

    return {
        "today": today.isoformat(),
        "total_activities": len(activities),
        "delayed_count": len(delayed),
        "on_track_count": len(on_track),
        "delayed_activities": delayed,
        "on_track_activities": on_track
    }


# ---------------------------------------------------------
# ACTIVITY SUMMARY
# ---------------------------------------------------------

@router.get("/activity-summary")
def activity_summary(
    project_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Activity)

    if project_id is not None:
        query = query.filter(
            Activity.project_id == project_id
        )

    activities = query.order_by(
        Activity.id.asc()
    ).all()

    result = []

    for activity in activities:

        result.append({
            "id": activity.id,
            "project_id": activity.project_id,
            "title": activity.title,
            "description": activity.description,
            "assigned_to": activity.assigned_to,
            "activity_date": (
                activity.activity_date.isoformat()
                if activity.activity_date
                else None
            ),
            "planned_end": (
                activity.planned_end.isoformat()
                if activity.planned_end
                else None
            ),
            "actual_start": (
                activity.actual_start.isoformat()
                if activity.actual_start
                else None
            ),
            "status": activity.status,
            "priority": activity.priority
        })

    return result


# ---------------------------------------------------------
# RESOURCE UTILIZATION
# ---------------------------------------------------------

@router.get("/resource-utilization")
def resource_utilization(
    project_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Activity)

    if project_id is not None:
        query = query.filter(
            Activity.project_id == project_id
        )

    activities = query.all()

    resources = defaultdict(
        lambda: {
            "total": 0,
            "completed": 0,
            "pending": 0
        }
    )

    for activity in activities:

        resource = (
            activity.assigned_to
            if activity.assigned_to
            else "Unassigned"
        )

        resources[resource]["total"] += 1

        if activity.status == "completed":
            resources[resource]["completed"] += 1

        if activity.status == "pending":
            resources[resource]["pending"] += 1

    result = []

    for resource, values in resources.items():

        total = values["total"]

        percentage = (
            round(
                (values["completed"] / total) * 100,
                2
            )
            if total > 0
            else 0
        )

        result.append({
            "resource": resource,
            "total": total,
            "completed": values["completed"],
            "pending": values["pending"],
            "utilization_percentage": percentage
        })

    return result


# ---------------------------------------------------------
# REPORT BY DATE PERIOD
# ---------------------------------------------------------

@router.get("/by-period")
def report_by_period(
    start_date: date = Query(...),
    end_date: date = Query(...),
    project_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    if start_date > end_date:

        raise HTTPException(
            status_code=400,
            detail="start_date cannot be after end_date"
        )

    query = db.query(Activity)

    if project_id is not None:
        query = query.filter(
            Activity.project_id == project_id
        )

    activities = query.filter(
        Activity.activity_date >= start_date,
        Activity.activity_date <= end_date
    ).order_by(
        Activity.activity_date.asc()
    ).all()

    return {
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "total_activities": len(activities),
        "activities": activities
    }


# ---------------------------------------------------------
# GENERATE ACTIVITY CSV REPORT
# ---------------------------------------------------------

@router.get("/generate")
def generate_report(
    project_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Activity)

    if project_id is not None:
        query = query.filter(
            Activity.project_id == project_id
        )

    activities = query.order_by(
        Activity.id.asc()
    ).all()

    filename = (
        f"project_report_"
        f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    )

    file_path = os.path.join(
        REPORT_DIR,
        filename
    )

    with open(
        file_path,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.writer(file)

        writer.writerow([
            "ID",
            "Project ID",
            "Title",
            "Assigned To",
            "Activity Date",
            "Planned End",
            "Actual Start",
            "Status",
            "Priority"
        ])

        for activity in activities:

            writer.writerow([
                activity.id,
                activity.project_id,
                activity.title,
                activity.assigned_to or "",
                activity.activity_date or "",
                activity.planned_end or "",
                activity.actual_start or "",
                activity.status,
                activity.priority
            ])

    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="text/csv"
    )


# ---------------------------------------------------------
# DOWNLOAD PROJECT PDF
# ---------------------------------------------------------

@router.get("/project-pdf")
def download_project_pdf(
    project_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
    except ImportError:

        raise HTTPException(
            status_code=500,
            detail=(
                "PDF support is not installed. "
                "Run: pip install reportlab"
            )
        )

    if project_id is not None:

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

        activities = (
            db.query(Activity)
            .filter(
                Activity.project_id == project_id
            )
            .all()
        )

        project_name = project.name

    else:

        project = (
            db.query(Project)
            .order_by(Project.id.asc())
            .first()
        )

        activities = (
            db.query(Activity)
            .order_by(Activity.id.asc())
            .all()
        )

        project_name = (
            project.name
            if project
            else "Project"
        )

    filename = (
        f"project_report_"
        f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    )

    file_path = os.path.join(
        REPORT_DIR,
        filename
    )

    pdf = canvas.Canvas(
        file_path,
        pagesize=A4
    )

    width, height = A4

    y = height - 50

    pdf.setFont(
        "Helvetica-Bold",
        18
    )

    pdf.drawString(
        50,
        y,
        "Project Report"
    )

    y -= 30

    pdf.setFont(
        "Helvetica",
        11
    )

    pdf.drawString(
        50,
        y,
        f"Project: {project_name}"
    )

    y -= 20

    total = len(activities)

    completed = sum(
        1
        for activity in activities
        if activity.status == "completed"
    )

    percentage = (
        round(
            (completed / total) * 100,
            2
        )
        if total > 0
        else 0
    )

    pdf.drawString(
        50,
        y,
        f"Total Activities: {total}"
    )

    y -= 18

    pdf.drawString(
        50,
        y,
        f"Completed Activities: {completed}"
    )

    y -= 18

    pdf.drawString(
        50,
        y,
        f"Overall Progress: {percentage}%"
    )

    y -= 35

    pdf.setFont(
        "Helvetica-Bold",
        10
    )

    pdf.drawString(
        50,
        y,
        "Activity"
    )

    pdf.drawString(
        260,
        y,
        "Status"
    )

    pdf.drawString(
        350,
        y,
        "Priority"
    )

    pdf.drawString(
        430,
        y,
        "Planned End"
    )

    y -= 18

    pdf.setFont(
        "Helvetica",
        9
    )

    for activity in activities:

        if y < 50:

            pdf.showPage()

            y = height - 50

            pdf.setFont(
                "Helvetica",
                9
            )

        title = activity.title[:32]

        pdf.drawString(
            50,
            y,
            title
        )

        pdf.drawString(
            260,
            y,
            activity.status or ""
        )

        pdf.drawString(
            350,
            y,
            activity.priority or ""
        )

        pdf.drawString(
            430,
            y,
            str(activity.planned_end or "")
        )

        y -= 16

    pdf.save()

    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/pdf"
    )