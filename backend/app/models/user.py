"""
User ORM Model.

Maps the `users` table to a Python class. Each instance of `User`
represents a single row in the database.

OOP Concepts Demonstrated:
    - **Encapsulation**: The password is stored as `password_hash`,
      never as plaintext.  Hashing logic lives in the auth service,
      not in the model — separation of concerns.
    - **Relationships**: SQLAlchemy `relationship()` provides
      object-oriented navigation (user.applications) that hides
      the underlying SQL JOIN from the caller.
"""

from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    """Registered user who can apply for jobs and save bookmarks."""

    __tablename__ = "users"

    # ── Primary Key ──────────────────────────────────────────────
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # ── Core Fields ──────────────────────────────────────────────
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(150), nullable=False)
    phone = Column(String(20), nullable=True)
    resume_url = Column(Text, nullable=True)

    # ── Timestamps ───────────────────────────────────────────────
    created_at = Column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # ── Relationships (ORM-level, not DB columns) ────────────────
    applications = relationship(
        "Application",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="select",
    )
    saved_jobs = relationship(
        "SavedJob",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="select",
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email='{self.email}')>"
