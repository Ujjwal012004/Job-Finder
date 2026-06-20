"""
Job ORM Model.

Central entity of the application.  Each row represents one job
posting, linked to a company via a foreign key.

OOP Concepts Demonstrated:
    - **Association**: Job "belongs to" a Company (many-to-one).
      The `company` relationship lets us write `job.company.name`
      instead of a manual JOIN — the ORM abstracts relational
      navigation into object attribute access.
    - **CHECK constraints via `CheckConstraint`**: Business rules
      (valid employment types, salary range logic) are declared
      in the model and enforced by the DBMS, not just app code.
"""

from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Numeric,
    Boolean,
    DateTime,
    ForeignKey,
    CheckConstraint,
)
from sqlalchemy.orm import relationship

from app.database import Base


class Job(Base):
    """A single job posting linked to a company."""

    __tablename__ = "jobs"

    # ── Table-level Constraints ──────────────────────────────────
    __table_args__ = (
        CheckConstraint(
            "employment_type IN ('full-time','part-time','contract','internship','freelance')",
            name="chk_employment_type",
        ),
        CheckConstraint(
            "experience_level IN ('entry','mid','senior','lead','executive')",
            name="chk_experience_level",
        ),
        CheckConstraint(
            "status IN ('active','closed','expired')",
            name="chk_job_status",
        ),
        CheckConstraint(
            "salary_min IS NULL OR salary_max IS NULL OR salary_min <= salary_max",
            name="chk_salary_range",
        ),
    )

    # ── Primary Key ──────────────────────────────────────────────
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # ── Foreign Key ──────────────────────────────────────────────
    company_id = Column(
        Integer,
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # ── Core Fields ──────────────────────────────────────────────
    title = Column(String(300), nullable=False, index=True)
    description = Column(Text, nullable=True)
    location = Column(String(255), nullable=True, index=True)

    employment_type = Column(String(50), nullable=False, default="full-time")
    experience_level = Column(String(50), nullable=True)

    salary_min = Column(Numeric(12, 2), nullable=True)
    salary_max = Column(Numeric(12, 2), nullable=True)
    salary_currency = Column(String(3), nullable=True, default="USD")

    source = Column(String(100), nullable=True)
    source_url = Column(Text, nullable=True)

    is_remote = Column(Boolean, nullable=False, default=False, index=True)
    status = Column(String(20), nullable=False, default="active", index=True)

    # ── Timestamps ───────────────────────────────────────────────
    posted_at = Column(DateTime, nullable=True)
    created_at = Column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # ── Relationships ────────────────────────────────────────────
    company = relationship("Company", back_populates="jobs")

    applications = relationship(
        "Application",
        back_populates="job",
        cascade="all, delete-orphan",
        lazy="select",
    )
    saved_by = relationship(
        "SavedJob",
        back_populates="job",
        cascade="all, delete-orphan",
        lazy="select",
    )

    def __repr__(self) -> str:
        return f"<Job(id={self.id}, title='{self.title}')>"
