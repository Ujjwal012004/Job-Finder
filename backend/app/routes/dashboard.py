"""
Dashboard Routes — Wires ApplicationTrackerService into API endpoints.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.auth import get_current_user
from app.services.application_tracker_service import ApplicationTrackerService
from app.schemas.dashboard import (
    DashboardResponse,
    PipelineStatsResponse,
    CompanyInsightResponse,
    TimelineEntryResponse,
    RecentActivityResponse,
)

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard & Analytics"])


@router.get("/", response_model=DashboardResponse)
def get_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get the complete application tracker dashboard.

    Returns pipeline stats, top companies, timeline, and recent activity
    in a single API call — optimized for the frontend to render the
    entire dashboard without multiple requests.
    """
    service = ApplicationTrackerService(db)
    dashboard = service.get_dashboard(current_user.id)

    return DashboardResponse(
        pipeline=PipelineStatsResponse(
            total=dashboard.pipeline.total,
            by_status=dashboard.pipeline.by_status,
            success_rate=dashboard.pipeline.success_rate,
            active_rate=dashboard.pipeline.active_rate,
            this_week=dashboard.pipeline.this_week,
            this_month=dashboard.pipeline.this_month,
        ),
        top_companies=[
            CompanyInsightResponse(
                company_name=c.company_name,
                company_id=c.company_id,
                application_count=c.application_count,
                statuses=c.statuses,
                latest_application_date=c.latest_application_date,
            )
            for c in dashboard.top_companies
        ],
        timeline=[
            TimelineEntryResponse(
                date=t.date,
                count=t.count,
                cumulative=t.cumulative,
            )
            for t in dashboard.timeline
        ],
        recent_activity=[
            RecentActivityResponse(**a)
            for a in dashboard.recent_activity
        ],
    )


@router.get("/pipeline", response_model=PipelineStatsResponse)
def get_pipeline_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get pipeline statistics only (lightweight)."""
    service = ApplicationTrackerService(db)
    stats = service.get_pipeline_stats(current_user.id)

    return PipelineStatsResponse(
        total=stats.total,
        by_status=stats.by_status,
        success_rate=stats.success_rate,
        active_rate=stats.active_rate,
        this_week=stats.this_week,
        this_month=stats.this_month,
    )
