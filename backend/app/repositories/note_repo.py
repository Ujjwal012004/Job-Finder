"""
ApplicationNote Repository.
"""

from typing import List

from sqlalchemy.orm import Session

from app.models.application_note import ApplicationNote
from app.repositories.base import BaseRepository


class ApplicationNoteRepository(BaseRepository[ApplicationNote]):
    """Encapsulates all database operations for application notes."""

    def __init__(self, db: Session):
        super().__init__(ApplicationNote, db)

    def get_by_application(
        self, application_id: int, skip: int = 0, limit: int = 50
    ) -> List[ApplicationNote]:
        """Fetch all notes for a specific application, newest first."""
        return (
            self._db.query(ApplicationNote)
            .filter(ApplicationNote.application_id == application_id)
            .order_by(ApplicationNote.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
