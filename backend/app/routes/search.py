"""
Search Routes — Wires JobSearchService into API endpoints.

This is where Phase 3's decoupled service meets the HTTP layer.
Notice how thin these route handlers are — they:
    1. Extract parameters from the request
    2. Instantiate the service (with injected DB session)
    3. Call a single service method
    4. Transform the result into the response schema

No business logic lives here.
"""

from typing import Optional
from decimal import Decimal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.auth import get_current_user, get_optional_current_user
from app.services.job_search_service import JobSearchService
from app.schemas.search import (
    SearchResponseSchema,
    SearchResultResponse,
    JobAggregationResponse,
)
from app.schemas.job import JobResponse

router = APIRouter(prefix="/api/search", tags=["Search & Discovery"])


@router.get("/jobs", response_model=SearchResponseSchema)
def search_jobs_advanced(
    keyword: Optional[str] = Query(None, description="Search title & description"),
    location: Optional[str] = Query(None, description="Filter by location"),
    employment_type: Optional[str] = Query(None, description="full-time, part-time, etc."),
    experience_level: Optional[str] = Query(None, description="entry, mid, senior, etc."),
    is_remote: Optional[bool] = Query(None, description="Remote jobs only"),
    salary_min: Optional[Decimal] = Query(None, description="Minimum salary"),
    salary_max: Optional[Decimal] = Query(None, description="Maximum salary"),
    company_name: Optional[str] = Query(None, description="Filter by company"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Results per page"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    """
    Advanced job search with relevance scoring and user context.

    Returns scored results enriched with is_saved/has_applied flags.
    """
    service = JobSearchService(db)
    result = service.search(
        keyword=keyword,
        location=location,
        employment_type=employment_type,
        experience_level=experience_level,
        is_remote=is_remote,
        salary_min=salary_min,
        salary_max=salary_max,
        company_name=company_name,
        page=page,
        page_size=page_size,
        user_id=current_user.id if current_user else None,
    )

    # Transform dataclass results into Pydantic response
    return SearchResponseSchema(
        results=[
            SearchResultResponse(
                job=JobResponse.model_validate(sr.job),
                relevance_score=sr.relevance_score,
                is_saved=sr.is_saved,
                has_applied=sr.has_applied,
            )
            for sr in result.results
        ],
        total_count=result.total_count,
        page=result.page,
        page_size=result.page_size,
        filters_applied=result.filters_applied,
    )


@router.get("/aggregations", response_model=JobAggregationResponse)
def get_job_aggregations(db: Session = Depends(get_db)):
    """
    Get aggregated job statistics (counts by type, level, location, etc.).

    Useful for rendering filter sidebar counts on the frontend.
    """
    service = JobSearchService(db)
    agg = service.get_aggregations()

    return JobAggregationResponse(
        total_jobs=agg.total_jobs,
        by_employment_type=agg.by_employment_type,
        by_experience_level=agg.by_experience_level,
        by_location=agg.by_location,
        remote_count=agg.remote_count,
        salary_range={
            "min": str(agg.salary_range.get("min", "")) if agg.salary_range.get("min") else None,
            "max": str(agg.salary_range.get("max", "")) if agg.salary_range.get("max") else None,
        },
    )


@router.get("/recommendations", response_model=list[SearchResultResponse])
def get_recommendations(
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get personalized job recommendations based on user's history.
    """
    service = JobSearchService(db)
    recs = service.get_recommendations(
        user_id=current_user.id,
        limit=limit,
    )

    return [
        SearchResultResponse(
            job=JobResponse.model_validate(sr.job),
            relevance_score=sr.relevance_score,
            is_saved=sr.is_saved,
            has_applied=sr.has_applied,
        )
        for sr in recs
    ]
