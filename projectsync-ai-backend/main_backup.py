from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import Base, engine

from routes.auth import router as auth_router
from fastapi import Depends
from dependencies import get_current_user
from routes.projects import router as projects_router
from models.user import User
from models.project import Project
from models.activity import Activity
from routes.activities import router as activities_router
from models.daily_report import DailyReport
from routes.daily_reports import router as daily_reports_router
from routes.schedule import router as schedule_router
from routes.dashboard import router as dashboard_router


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