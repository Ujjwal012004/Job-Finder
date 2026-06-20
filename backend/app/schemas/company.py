"""
Company Pydantic Schemas.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class CompanyCreate(BaseModel):
    """Schema for creating a new company."""
    name: str
    website: Optional[str] = None
    logo_url: Optional[str] = None
    industry: Optional[str] = None
    description: Optional[str] = None


class CompanyUpdate(BaseModel):
    """Schema for updating a company. All fields optional."""
    name: Optional[str] = None
    website: Optional[str] = None
    logo_url: Optional[str] = None
    industry: Optional[str] = None
    description: Optional[str] = None


class CompanyResponse(BaseModel):
    """Public-facing company data."""
    id: int
    name: str
    website: Optional[str] = None
    logo_url: Optional[str] = None
    industry: Optional[str] = None
    description: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
