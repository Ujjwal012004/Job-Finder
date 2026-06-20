"""
User Pydantic Schemas.

These are Data Transfer Objects (DTOs) — they define the shape of
data flowing in and out of the API. They are NOT ORM models.

OOP Concept — Separation of Concerns:
    ORM models map to database tables (persistence layer).
    Pydantic schemas validate HTTP payloads (presentation layer).
    Keeping them separate means:
        - You can change DB columns without breaking the API contract.
        - You never accidentally expose internal fields (like password_hash).
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, ConfigDict


# ── Request Schemas (what the client sends) ──────────────────────

class UserCreate(BaseModel):
    """Schema for user registration."""
    email: str
    password: str
    full_name: str
    phone: Optional[str] = None
    resume_url: Optional[str] = None


class UserUpdate(BaseModel):
    """Schema for updating user profile. All fields optional."""
    full_name: Optional[str] = None
    phone: Optional[str] = None
    resume_url: Optional[str] = None


class UserLogin(BaseModel):
    """Schema for login request."""
    email: str
    password: str


# ── Response Schemas (what the API returns) ──────────────────────

class UserResponse(BaseModel):
    """
    Public-facing user data.
    Note: password_hash is intentionally excluded — never expose
    secrets in API responses.
    """
    id: int
    email: str
    full_name: str
    phone: Optional[str] = None
    resume_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    """JWT token response."""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Decoded token payload."""
    user_id: Optional[int] = None
