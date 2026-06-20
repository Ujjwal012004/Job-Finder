"""
Job Pydantic Schemas.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.schemas.company import CompanyResponse


class JobCreate(BaseModel):
    """Schema for creating a new job posting."""
    company_id: int
    title: str
    description: Optional[str] = None
    location: Optional[str] = None
    employment_type: str = "full-time"
    experience_level: Optional[str] = None
    salary_min: Optional[Decimal] = None
    salary_max: Optional[Decimal] = None
    salary_currency: Optional[str] = "USD"
    source: Optional[str] = None
    source_url: Optional[str] = None
    is_remote: bool = False
    status: str = "active"
    posted_at: Optional[datetime] = None


class JobUpdate(BaseModel):
    """Schema for updating a job. All fields optional."""
    title: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    employment_type: Optional[str] = None
    experience_level: Optional[str] = None
    salary_min: Optional[Decimal] = None
    salary_max: Optional[Decimal] = None
    salary_currency: Optional[str] = None
    source: Optional[str] = None
    source_url: Optional[str] = None
    is_remote: Optional[bool] = None
    status: Optional[str] = None


class JobResponse(BaseModel):
    """Public-facing job data with nested company info."""
    id: int
    company_id: int
    title: str
    description: Optional[str] = None
    location: Optional[str] = None
    employment_type: str
    experience_level: Optional[str] = None
    salary_min: Optional[Decimal] = None
    salary_max: Optional[Decimal] = None
    salary_currency: Optional[str] = None
    source: Optional[str] = None
    source_url: Optional[str] = None
    is_remote: bool
    status: str
    posted_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    # Nested company object — demonstrates ORM relationship serialization
    company: Optional[CompanyResponse] = None

    model_config = ConfigDict(from_attributes=True)


class JobSearchParams(BaseModel):
    """Query parameters for searching/filtering jobs."""
    keyword: Optional[str] = None
    location: Optional[str] = None
    employment_type: Optional[str] = None
    experience_level: Optional[str] = None
    is_remote: Optional[bool] = None
    salary_min: Optional[Decimal] = None
    status: str = "active"
    skip: int = 0
    limit: int = 20
