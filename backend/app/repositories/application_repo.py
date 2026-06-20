"""
Application Repository — handles application-specific queries.
"""

from typing import Optional, List

from sqlalchemy.orm import Session

from app.models.application import Application
from app.repositories.base import BaseRepository


class ApplicationRepository(BaseRepository[Application]):
    """Encapsulates all database operations for the Application entity."""

    def __init__(self, db: Session):
        super().__init__(Application, db)

    def get_by_user(self, user_id: int, skip: int = 0, limit: int = 50) -> List[Application]:
        """Fetch all applications for a specific user."""
        return (
            self._db.query(Application)
            .filter(Application.user_id == user_id)
            .order_by(Application.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_user_and_job(self, user_id: int, job_id: int) -> Optional[Application]:
        """Check if a user has already applied to a specific job."""
        return (
            self._db.query(Application)
            .filter(Application.user_id == user_id, Application.job_id == job_id)
            .first()
        )

    def count_by_user(self, user_id: int) -> int:
        """Count total applications for a user."""
        return self._db.query(Application).filter(Application.user_id == user_id).count()
