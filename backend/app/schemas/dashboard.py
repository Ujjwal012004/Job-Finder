"""
Dashboard Pydantic Schemas.

Serializes ApplicationTrackerService results for the frontend.
"""

from typing import Optional, List, Dict
from datetime import datetime

from pydantic import BaseModel


class PipelineStatsResponse(BaseModel):
    """Application pipeline statistics."""
    total: int = 0
    by_status: Dict[str, int] = {}
    success_rate: float = 0.0
    active_rate: float = 0.0
    this_week: int = 0
    this_month: int = 0


class CompanyInsightResponse(BaseModel):
    """Application activity for a company."""
    company_name: str = ""
    company_id: int = 0
    application_count: int = 0
    statuses: Dict[str, int] = {}
    latest_application_date: Optional[datetime] = None


class TimelineEntryResponse(BaseModel):
    """Daily application count."""
    date: str = ""
    count: int = 0
    cumulative: int = 0


class RecentActivityResponse(BaseModel):
    """Recent application activity item."""
    application_id: int
    job_title: str
    company_name: str
    status: str
    applied_on: Optional[str] = None
    updated_at: Optional[str] = None


class DashboardResponse(BaseModel):
    """Complete dashboard data."""
    pipeline: PipelineStatsResponse
    top_companies: List[CompanyInsightResponse] = []
    timeline: List[TimelineEntryResponse] = []
    recent_activity: List[RecentActivityResponse] = []


class ImportResultResponse(BaseModel):
    """Result of a data import operation."""
    total_processed: int = 0
    created: int = 0
    skipped_duplicate: int = 0
    skipped_invalid: int = 0
    errors: List[str] = []
