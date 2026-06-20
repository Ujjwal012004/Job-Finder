"""
Company Repository.
"""

from typing import Optional

from sqlalchemy.orm import Session

from app.models.company import Company
from app.repositories.base import BaseRepository


class CompanyRepository(BaseRepository[Company]):
    """Encapsulates all database operations for the Company entity."""

    def __init__(self, db: Session):
        super().__init__(Company, db)

    def find_by_name(self, name: str) -> Optional[Company]:
        """Look up a company by exact name."""
        return self._db.query(Company).filter(Company.name == name).first()
