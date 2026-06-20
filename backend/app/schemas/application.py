"""
Application & SavedJob & ApplicationNote Pydantic Schemas.
"""

from datetime import date, datetime
from typing import Optional, List

from pydantic import BaseModel, ConfigDict


# ── Application Schemas ──────────────────────────────────────────

class ApplicationCreate(BaseModel):
    """Schema for submitting a job application."""
    job_id: int
    cover_letter: Optional[str] = None
    resume_snapshot_url: Optional[str] = None


class ApplicationUpdate(BaseModel):
    """Schema for updating an application (e.g., changing status)."""
    status: Optional[str] = None
    cover_letter: Optional[str] = None
    resume_snapshot_url: Optional[str] = None


class ApplicationResponse(BaseModel):
    """Public-facing application data."""
    id: int
    user_id: int
    job_id: int
    status: str
    applied_on: date
    cover_letter: Optional[str] = None
    resume_snapshot_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ── Saved Job Schemas ────────────────────────────────────────────

class SavedJobCreate(BaseModel):
    """Schema for bookmarking a job."""
    job_id: int


class SavedJobResponse(BaseModel):
    """Public-facing saved job data."""
    id: int
    user_id: int
    job_id: int
    saved_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ── Application Note Schemas ─────────────────────────────────────

class ApplicationNoteCreate(BaseModel):
    """Schema for adding a note to an application."""
    content: str
    note_type: str = "general"


class ApplicationNoteResponse(BaseModel):
    """Public-facing note data."""
    id: int
    application_id: int
    content: str
    note_type: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
