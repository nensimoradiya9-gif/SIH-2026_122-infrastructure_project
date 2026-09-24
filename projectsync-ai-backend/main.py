from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from database import Base, engine

from models.user import User
from models.project import Project
from models.activity import Activity
from models.daily_report import DailyReport
from models.alert import Alert

from routes.auth import router as auth_router
from routes.projects import router as projects_router
from routes.activities import router as activities_router
from routes.daily_reports import router as daily_reports_router
from routes.schedule import router as schedule_router
from routes.dashboard import router as dashboard_router

from dependencies import get_current_user
from routes.alerts import router as alerts_router
from routes.analytics import router as analytics_router
from routes.ai_matching import router as ai_matching_router
from routes.reports import router as reports_router
from models.knowledge import Knowledge
from routes.knowledge import router as knowledge_router
from models.settings import Settings
from routes.settings import router as settings_router
from models.activity_capture import ActivityCapture
from routes.activity_capture import router as activity_capture_router



Base.metadata.create_all(bind=engine)

app = FastAPI(title="ProjectSync AI Backend")


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth_router)
app.include_router(projects_router)
app.include_router(activities_router)
app.include_router(daily_reports_router)
app.include_router(schedule_router)
app.include_router(dashboard_router)
app.include_router(alerts_router)
app.include_router(analytics_router)
app.include_router(ai_matching_router)
app.include_router(reports_router)
app.include_router(knowledge_router)
app.include_router(settings_router)
app.include_router(activity_capture_router)


@app.get("/api/protected")
def protected_route(current_user=Depends(get_current_user)):
    return {
        "message": "You are authenticated!",
        "user": current_user
    }


@app.get("/")
def home():
    return {
        "message": "ProjectSync AI Backend is running"
    }


@app.get("/api/health")
def health():
    return {
        "status": "ok"
    }