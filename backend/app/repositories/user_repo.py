"""
User Repository — extends BaseRepository with user-specific queries.

OOP Concept — Inheritance + Extension:
    UserRepository inherits generic CRUD from BaseRepository[User]
    and adds domain-specific methods (find_by_email) without
    modifying the parent class.
"""

from typing import Optional

from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Encapsulates all database operations for the User entity."""

    def __init__(self, db: Session):
        super().__init__(User, db)

    def find_by_email(self, email: str) -> Optional[User]:
        """
        Look up a user by email address.
        Used during login and registration (duplicate check).
        """
        return self._db.query(User).filter(User.email == email).first()
