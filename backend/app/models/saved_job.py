"""
SavedJob ORM Model (Bookmark / Junction Table).

This is a classic **association table** that resolves the many-to-many
relationship between Users and Jobs:
    - A user can save (bookmark) many jobs.
    - A job can be saved by many users.

Without this table, you'd need a comma-separated list of job IDs in
the `users` table — violating First Normal Form (1NF).

The UNIQUE constraint on (user_id, job_id) ensures a user can only
bookmark the same job once.
"""

from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.database import Base


class SavedJob(Base):
    """Bookmark linking a user to a saved job posting."""

    __tablename__ = "saved_jobs"

    __table_args__ = (
        UniqueConstraint("user_id", "job_id", name="uq_user_saved_job"),
    )

    # ── Primary Key ──────────────────────────────────────────────
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # ── Foreign Keys ─────────────────────────────────────────────
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    job_id = Column(
        Integer,
        ForeignKey("jobs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # ── Timestamps ───────────────────────────────────────────────
    saved_at = Column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    # ── Relationships ────────────────────────────────────────────
    user = relationship("User", back_populates="saved_jobs")
    job = relationship("Job", back_populates="saved_by")

    def __repr__(self) -> str:
        return f"<SavedJob(user_id={self.user_id}, job_id={self.job_id})>"
