"""
Application ORM Model.

Represents a user's application to a specific job.  The UNIQUE
constraint on (user_id, job_id) is a database-level invariant
that prevents duplicate applications — even if app logic has bugs,
the DBMS will reject the INSERT.

OOP Concepts Demonstrated:
    - **Composition**: An Application "has" notes (one-to-many).
      If the application is deleted, its notes are cascade-deleted.
      This models a strong ownership ("whole–part") relationship.
    - **UniqueConstraint as a class-level declaration**: The
      `__table_args__` tuple shows how ORM models can declaratively
      express relational constraints, keeping schema logic co-located
      with the domain entity.
"""

from datetime import date, datetime, timezone

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Date,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    CheckConstraint,
)
from sqlalchemy.orm import relationship

from app.database import Base


class Application(Base):
    """A user's application to a job posting."""

    __tablename__ = "applications"

    __table_args__ = (
        UniqueConstraint("user_id", "job_id", name="uq_user_job_application"),
        CheckConstraint(
            "status IN ('applied','screening','interviewing','offered','accepted','rejected','withdrawn')",
            name="chk_application_status",
        ),
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

    # ── Core Fields ──────────────────────────────────────────────
    status = Column(String(30), nullable=False, default="applied", index=True)
    applied_on = Column(Date, nullable=False, default=date.today)
    cover_letter = Column(Text, nullable=True)
    resume_snapshot_url = Column(Text, nullable=True)

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

    # ── Relationships ────────────────────────────────────────────
    user = relationship("User", back_populates="applications")
    job = relationship("Job", back_populates="applications")

    notes = relationship(
        "ApplicationNote",
        back_populates="application",
        cascade="all, delete-orphan",
        lazy="select",
    )

    def __repr__(self) -> str:
        return f"<Application(id={self.id}, user_id={self.user_id}, job_id={self.job_id}, status='{self.status}')>"
