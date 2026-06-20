"""
Company ORM Model.

Extracted as a separate entity to achieve Third Normal Form (3NF):
company attributes (name, website, logo) depend on the company's
identity, NOT on any particular job posting.  Without this table,
`jobs` would contain transitive dependencies:
    job_id → company_name → company_website   (violates 3NF)

By normalizing, we also gain:
    - Single point of update for company info
    - Referential integrity via foreign key from `jobs`
    - Reduced data redundancy across thousands of job rows
"""

from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship

from app.database import Base


class Company(Base):
    """Organization that posts job listings."""

    __tablename__ = "companies"

    # ── Primary Key ──────────────────────────────────────────────
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # ── Core Fields ──────────────────────────────────────────────
    name = Column(String(255), unique=True, nullable=False, index=True)
    website = Column(String(500), nullable=True)
    logo_url = Column(Text, nullable=True)
    industry = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)

    # ── Timestamps ───────────────────────────────────────────────
    created_at = Column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    # ── Relationships ────────────────────────────────────────────
    jobs = relationship(
        "Job",
        back_populates="company",
        cascade="all, delete-orphan",
        lazy="select",
    )

    def __repr__(self) -> str:
        return f"<Company(id={self.id}, name='{self.name}')>"
