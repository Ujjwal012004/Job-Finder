"""
Job Routes — CRUD + Search for job listings.
"""

from typing import List, Optional
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.job import JobCreate, JobUpdate, JobResponse
from app.repositories.job_repo import JobRepository

router = APIRouter(prefix="/api/jobs", tags=["Jobs"])


@router.post("/", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
def create_job(job_data: JobCreate, db: Session = Depends(get_db)):
    """Create a new job posting."""
    return JobRepository(db).create(job_data.model_dump())


@router.get("/", response_model=List[JobResponse])
def search_jobs(
    keyword: Optional[str] = Query(None, description="Search title and description"),
    location: Optional[str] = Query(None),
    employment_type: Optional[str] = Query(None),
    experience_level: Optional[str] = Query(None),
    is_remote: Optional[bool] = Query(None),
    salary_min: Optional[Decimal] = Query(None, description="Minimum salary filter"),
    status_filter: str = Query("active", alias="status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Search jobs with optional filters and pagination."""
    repo = JobRepository(db)
    return repo.search(
        keyword=keyword,
        location=location,
        employment_type=employment_type,
        experience_level=experience_level,
        is_remote=is_remote,
        salary_min=salary_min,
        status=status_filter,
        skip=skip,
        limit=limit,
    )


@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: int, db: Session = Depends(get_db)):
    """Get a single job with company details."""
    job = JobRepository(db).get_by_id_with_company(job_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    return job


@router.put("/{job_id}", response_model=JobResponse)
def update_job(job_id: int, update_data: JobUpdate, db: Session = Depends(get_db)):
    """Update a job posting."""
    updated = JobRepository(db).update(job_id, update_data.model_dump(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    return updated


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job(job_id: int, db: Session = Depends(get_db)):
    """Delete a job posting."""
    if not JobRepository(db).delete(job_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
