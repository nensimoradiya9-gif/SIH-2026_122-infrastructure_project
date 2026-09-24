from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from database import SessionLocal
from models.alert import Alert


router = APIRouter(
    prefix="/api/alerts",
    tags=["Alerts"]
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


# ---------------------------------------------------------
# RESPONSE / REQUEST MODEL
# ---------------------------------------------------------

class AlertRequest(BaseModel):
    title: str
    severity: str
    message: str
    time_label: Optional[str] = None
    status: Optional[str] = "unread"


# ---------------------------------------------------------
# GET ALL ALERTS
# ---------------------------------------------------------

@router.get("/")
def get_alerts(
    db: Session = Depends(get_db)
):
    alerts = (
        db.query(Alert)
        .order_by(Alert.id.desc())
        .all()
    )

    total = len(alerts)

    critical = sum(
        1
        for alert in alerts
        if alert.severity == "critical"
    )

    warnings = sum(
        1
        for alert in alerts
        if alert.severity == "warning"
    )

    info = sum(
        1
        for alert in alerts
        if alert.severity == "info"
    )

    return {
        "total": total,
        "critical": critical,
        "warnings": warnings,
        "info": info,
        "alerts": alerts
    }


# ---------------------------------------------------------
# GET ALERTS BY SEVERITY
# ---------------------------------------------------------

@router.get("/severity/{severity}")
def get_alerts_by_severity(
    severity: str,
    db: Session = Depends(get_db)
):

    allowed = [
        "critical",
        "warning",
        "info"
    ]

    if severity not in allowed:
        raise HTTPException(
            status_code=400,
            detail="Invalid severity"
        )

    return (
        db.query(Alert)
        .filter(Alert.severity == severity)
        .order_by(Alert.id.desc())
        .all()
    )


# ---------------------------------------------------------
# GET SINGLE ALERT
# ---------------------------------------------------------

@router.get("/{alert_id}")
def get_alert(
    alert_id: int,
    db: Session = Depends(get_db)
):

    alert = (
        db.query(Alert)
        .filter(Alert.id == alert_id)
        .first()
    )

    if not alert:
        raise HTTPException(
            status_code=404,
            detail="Alert not found"
        )

    return alert


# ---------------------------------------------------------
# CREATE ALERT
# ---------------------------------------------------------

@router.post("/")
def create_alert(
    data: AlertRequest,
    db: Session = Depends(get_db)
):

    allowed = [
        "critical",
        "warning",
        "info"
    ]

    if data.severity not in allowed:
        raise HTTPException(
            status_code=400,
            detail="Severity must be critical, warning, or info"
        )

    alert = Alert(
        title=data.title,
        severity=data.severity,
        message=data.message,
        time_label=data.time_label,
        status=data.status
    )

    db.add(alert)
    db.commit()
    db.refresh(alert)

    return alert


# ---------------------------------------------------------
# MARK ALERT AS READ / REVIEWED
# ---------------------------------------------------------

@router.put("/{alert_id}/review")
def review_alert(
    alert_id: int,
    db: Session = Depends(get_db)
):

    alert = (
        db.query(Alert)
        .filter(Alert.id == alert_id)
        .first()
    )

    if not alert:
        raise HTTPException(
            status_code=404,
            detail="Alert not found"
        )

    alert.status = "reviewed"

    db.commit()
    db.refresh(alert)

    return {
        "message": "Alert reviewed successfully",
        "alert": alert
    }


# ---------------------------------------------------------
# DELETE ALERT
# ---------------------------------------------------------

@router.delete("/{alert_id}")
def delete_alert(
    alert_id: int,
    db: Session = Depends(get_db)
):

    alert = (
        db.query(Alert)
        .filter(Alert.id == alert_id)
        .first()
    )

    if not alert:
        raise HTTPException(
            status_code=404,
            detail="Alert not found"
        )

    db.delete(alert)
    db.commit()

    return {
        "message": "Alert deleted successfully"
    }


# ---------------------------------------------------------
# CREATE DEMO ALERT DATA
# ---------------------------------------------------------

@router.post("/seed-demo")
def seed_demo_alerts(
    db: Session = Depends(get_db)
):

    existing_count = db.query(Alert).count()

    if existing_count > 0:
        return {
            "message": "Alerts already contain data",
            "existing_alerts": existing_count
        }

    demo_alerts = [

        # -------------------------
        # 4 CRITICAL
        # -------------------------

        Alert(
            title="Delay in Welding",
            severity="critical",
            message="Activity W-006 is 3 days behind. Material delay reported.",
            time_label="2 hours ago",
            status="unread"
        ),

        Alert(
            title="Critical Activity Delay",
            severity="critical",
            message="Structural work activity has exceeded its planned end date.",
            time_label="3 hours ago",
            status="unread"
        ),

        Alert(
            title="Material Delivery Delay",
            severity="critical",
            message="Required project material has not arrived at the site.",
            time_label="5 hours ago",
            status="unread"
        ),

        Alert(
            title="Schedule Risk Detected",
            severity="critical",
            message="Multiple pending activities may affect the planned project schedule.",
            time_label="7 hours ago",
            status="unread"
        ),

        # -------------------------
        # 5 WARNING
        # -------------------------

        Alert(
            title="Low Progress",
            severity="warning",
            message="Pipe Laying (P-001) is below the planned progress threshold.",
            time_label="4 hours ago",
            status="unread"
        ),

        Alert(
            title="Pending High Priority Activity",
            severity="warning",
            message="A high priority activity is still pending.",
            time_label="5 hours ago",
            status="unread"
        ),

        Alert(
            title="Upcoming Planned End",
            severity="warning",
            message="An activity is approaching its planned completion date.",
            time_label="8 hours ago",
            status="unread"
        ),

        Alert(
            title="Resource Assignment Missing",
            severity="warning",
            message="One or more activities do not have an assigned resource.",
            time_label="10 hours ago",
            status="unread"
        ),

        Alert(
            title="Daily Report Pending",
            severity="warning",
            message="A daily project report has not been submitted.",
            time_label="12 hours ago",
            status="unread"
        ),

        # -------------------------
        # 3 INFO
        # -------------------------

        Alert(
            title="Weather Impact",
            severity="info",
            message="Heavy rain may affect excavation work.",
            time_label="1 day ago",
            status="unread"
        ),

        Alert(
            title="Schedule Updated",
            severity="info",
            message="The latest project schedule information has been updated.",
            time_label="1 day ago",
            status="unread"
        ),

        Alert(
            title="Daily Report Submitted",
            severity="info",
            message="Today's daily project report has been successfully submitted.",
            time_label="2 days ago",
            status="unread"
        )
    ]

    db.add_all(demo_alerts)
    db.commit()

    return {
        "message": "Demo alerts created successfully",
        "total_created": len(demo_alerts)
    }