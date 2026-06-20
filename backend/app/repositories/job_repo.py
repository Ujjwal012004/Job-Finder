"""
Job Repository — extends BaseRepository with search/filter capabilities.

This is the most complex repository because job searching involves
dynamic query composition based on user-provided filters.

OOP Concept — Method Specialization:
    The `search()` method demonstrates how a subclass can add
    significantly more complex behavior while still reusing the
    parent's simple CRUD methods for basic operations.
"""

from typing import Optional, List
from decimal import Decimal

from sqlalchemy.orm import Session, joinedload

from app.models.job import Job
from app.repositories.base import BaseRepository


class JobRepository(BaseRepository[Job]):
    """Encapsulates all database operations for the Job entity."""

    def __init__(self, db: Session):
        super().__init__(Job, db)

    def get_by_id_with_company(self, job_id: int) -> Optional[Job]:
        """
        Fetch a job with its company eagerly loaded.
        Avoids the N+1 query problem by using `joinedload`.
        """
        return (
            self._db.query(Job)
            .options(joinedload(Job.company))
            .filter(Job.id == job_id)
            .first()
        )

    def search(
        self,
        keyword: Optional[str] = None,
        location: Optional[str] = None,
        employment_type: Optional[str] = None,
        experience_level: Optional[str] = None,
        is_remote: Optional[bool] = None,
        salary_min: Optional[Decimal] = None,
        status: str = "active",
        skip: int = 0,
        limit: int = 20,
    ) -> List[Job]:
        """
        Dynamic search with optional filters.

        Builds the SQL query incrementally — each filter is only
        applied if the caller provided it. This is the Query Builder
        pattern, a natural fit for ORM-based search endpoints.
        """
        query = self._db.query(Job).options(joinedload(Job.company))

        # Apply filters conditionally
        if keyword:
            query = query.filter(
                Job.title.ilike(f"%{keyword}%")
                | Job.description.ilike(f"%{keyword}%")
            )
        if location:
            query = query.filter(Job.location.ilike(f"%{location}%"))
        if employment_type:
            query = query.filter(Job.employment_type == employment_type)
        if experience_level:
            query = query.filter(Job.experience_level == experience_level)
        if is_remote is not None:
            query = query.filter(Job.is_remote == is_remote)
        if salary_min is not None:
            query = query.filter(Job.salary_max >= salary_min)
        if status:
            query = query.filter(Job.status == status)

        return query.order_by(Job.created_at.desc()).offset(skip).limit(limit).all()

    def count_search_results(
        self,
        keyword: Optional[str] = None,
        location: Optional[str] = None,
        employment_type: Optional[str] = None,
        experience_level: Optional[str] = None,
        is_remote: Optional[bool] = None,
        salary_min: Optional[Decimal] = None,
        status: str = "active",
    ) -> int:
        """Count total results for a search (for pagination metadata)."""
        query = self._db.query(Job)

        if keyword:
            query = query.filter(
                Job.title.ilike(f"%{keyword}%")
                | Job.description.ilike(f"%{keyword}%")
            )
        if location:
            query = query.filter(Job.location.ilike(f"%{location}%"))
        if employment_type:
            query = query.filter(Job.employment_type == employment_type)
        if experience_level:
            query = query.filter(Job.experience_level == experience_level)
        if is_remote is not None:
            query = query.filter(Job.is_remote == is_remote)
        if salary_min is not None:
            query = query.filter(Job.salary_max >= salary_min)
        if status:
            query = query.filter(Job.status == status)

        return query.count()
