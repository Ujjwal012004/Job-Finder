"""
Search & Discovery Pydantic Schemas.

These schemas serialize the dataclass results from JobSearchService
into JSON-compatible API responses.
"""

from typing import Optional, List, Dict, Any
from decimal import Decimal
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.schemas.job import JobResponse


class SearchResultResponse(BaseModel):
    """A single search result with relevance metadata."""
    job: JobResponse
    relevance_score: float = 0.0
    is_saved: bool = False
    has_applied: bool = False


class SearchResponseSchema(BaseModel):
    """Paginated search response with metadata."""
    results: List[SearchResultResponse] = []
    total_count: int = 0
    page: int = 1
    page_size: int = 20
    filters_applied: Dict[str, Any] = {}


class JobAggregationResponse(BaseModel):
    """Aggregated job statistics."""
    total_jobs: int = 0
    by_employment_type: Dict[str, int] = {}
    by_experience_level: Dict[str, int] = {}
    by_location: Dict[str, int] = {}
    remote_count: int = 0
    salary_range: Dict[str, Optional[str]] = {}
