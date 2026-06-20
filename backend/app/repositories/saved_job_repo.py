"""
SavedJob Repository.
"""

from typing import Optional, List

from sqlalchemy.orm import Session

from app.models.saved_job import SavedJob
from app.repositories.base import BaseRepository


class SavedJobRepository(BaseRepository[SavedJob]):
    """Encapsulates all database operations for saved/bookmarked jobs."""

    def __init__(self, db: Session):
        super().__init__(SavedJob, db)

    def get_by_user(self, user_id: int, skip: int = 0, limit: int = 50) -> List[SavedJob]:
        """Fetch all bookmarked jobs for a user."""
        return (
            self._db.query(SavedJob)
            .filter(SavedJob.user_id == user_id)
            .order_by(SavedJob.saved_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def find_bookmark(self, user_id: int, job_id: int) -> Optional[SavedJob]:
        """Check if a user has already bookmarked a specific job."""
        return (
            self._db.query(SavedJob)
            .filter(SavedJob.user_id == user_id, SavedJob.job_id == job_id)
            .first()
        )
