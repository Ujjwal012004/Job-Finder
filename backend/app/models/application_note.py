"""
ApplicationNote ORM Model.

A child entity of Application, modelling the one-to-many
relationship: one application can have many notes.

Design rationale for a separate table:
    - Notes have variable cardinality (0 to many per application).
    - Storing them as a JSON blob in `applications` would violate 1NF
      and make querying/filtering individual notes impossible in SQL.
    - The `note_type` column enables categorized filtering
      (e.g., "show me all my interview_prep notes across applications").
"""

from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
    CheckConstraint,
)
from sqlalchemy.orm import relationship

from app.database import Base


class ApplicationNote(Base):
    """Timestamped note attached to a job application."""

    __tablename__ = "application_notes"

    __table_args__ = (
        CheckConstraint(
            "note_type IN ('general','interview_prep','follow_up','feedback')",
            name="chk_note_type",
        ),
    )

    # ── Primary Key ──────────────────────────────────────────────
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # ── Foreign Key ──────────────────────────────────────────────
    application_id = Column(
        Integer,
        ForeignKey("applications.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # ── Core Fields ──────────────────────────────────────────────
    content = Column(Text, nullable=False)
    note_type = Column(String(30), nullable=False, default="general")

    # ── Timestamps ───────────────────────────────────────────────
    created_at = Column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    # ── Relationships ────────────────────────────────────────────
    application = relationship("Application", back_populates="notes")

    def __repr__(self) -> str:
        return f"<ApplicationNote(id={self.id}, type='{self.note_type}')>"
