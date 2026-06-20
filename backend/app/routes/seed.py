"""
Seed Routes — Wires JobDataService for database seeding.

These endpoints are for development/demo purposes.
In production, you'd gate them behind admin auth.
"""

from typing import List, Dict, Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.job_data_service import JobDataService
from app.schemas.dashboard import ImportResultResponse

router = APIRouter(prefix="/api/seed", tags=["Data Seeding"])


@router.post("/jobs", response_model=ImportResultResponse)
def seed_sample_jobs(db: Session = Depends(get_db)):
    """
    Seed the database with 15 realistic sample job listings.

    Idempotent — running twice won't create duplicates because
    the service checks for existing title+company combinations.
    """
    service = JobDataService(db)
    result = service.seed_sample_data()

    return ImportResultResponse(
        total_processed=result.total_processed,
        created=result.created,
        skipped_duplicate=result.skipped_duplicate,
        skipped_invalid=result.skipped_invalid,
        errors=result.errors,
    )


@router.post("/import", response_model=ImportResultResponse)
def import_jobs(
    jobs: List[Dict[str, Any]],
    db: Session = Depends(get_db),
):
    """
    Import jobs from a JSON payload.

    Accepts an array of job objects with fields:
        - company_name (required)
        - title (required)
        - description, location, employment_type, etc.
    """
    service = JobDataService(db)
    result = service.import_jobs(jobs)

    return ImportResultResponse(
        total_processed=result.total_processed,
        created=result.created,
        skipped_duplicate=result.skipped_duplicate,
        skipped_invalid=result.skipped_invalid,
        errors=result.errors,
    )
