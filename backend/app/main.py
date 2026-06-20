"""
Job Finder API — Main Application Entry Point.

This is the composition root where all components are wired together.
FastAPI's `include_router` aggregates routes from different modules,
demonstrating the Single Responsibility Principle: each route module
handles one domain entity, and `main.py` only handles assembly.

Run with:
    uvicorn app.main:app --reload
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import engine, Base

# Import all models so Base.metadata knows about every table
from app.models import User, Company, Job, Application, SavedJob, ApplicationNote  # noqa: F401

# Import route modules
from app.routes import auth, users, companies, jobs, applications, search, dashboard, seed

# ── Create Tables ────────────────────────────────────────────────
# In production, use Alembic migrations instead of create_all().
# This is convenient for development with SQLite.
Base.metadata.create_all(bind=engine)

# ── App Instance ─────────────────────────────────────────────────
app = FastAPI(
    title=settings.APP_NAME,
    description="Search, save, track, and manage job applications.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS Middleware ──────────────────────────────────────────────
# Allow the React frontend (running on a different port) to call the API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Register Routers ────────────────────────────────────────────
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(companies.router)
app.include_router(jobs.router)
app.include_router(applications.router)
app.include_router(search.router)
app.include_router(dashboard.router)
app.include_router(seed.router)


# ── Health Check ─────────────────────────────────────────────────
@app.get("/", tags=["Health"])
def health_check():
    """Root endpoint for health/readiness checks."""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": "1.0.0",
    }
