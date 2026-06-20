"""
Base Repository — Generic CRUD operations.

OOP Concepts Demonstrated:

1. **Generics / Parametric Polymorphism**:
   `BaseRepository[ModelType]` is parameterized by the ORM model class.
   Subclasses like `UserRepository(BaseRepository[User])` inherit all
   CRUD methods without re-implementing them.

2. **Encapsulation**:
   The database session (`self._db`) is a private attribute. External
   code never touches it directly — all DB access goes through the
   repository's public methods. This is the Repository Pattern from
   Domain-Driven Design (DDD).

3. **Open/Closed Principle (SOLID)**:
   The base class is open for extension (subclasses can add
   domain-specific queries) but closed for modification (core
   CRUD logic doesn't change).

4. **Dependency Injection**:
   The DB session is injected via the constructor, not created
   internally. This makes the repository testable — in unit tests,
   you can inject a mock session.
"""

from typing import TypeVar, Generic, Type, Optional, List

from sqlalchemy.orm import Session

from app.database import Base

# TypeVar bound to Base ensures only ORM models can be used
ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """
    Abstract base repository providing CRUD operations for any ORM model.

    Usage:
        class UserRepository(BaseRepository[User]):
            def __init__(self, db: Session):
                super().__init__(User, db)

            def find_by_email(self, email: str) -> Optional[User]:
                # Domain-specific query extension
                ...
    """

    def __init__(self, model: Type[ModelType], db: Session):
        """
        Args:
            model: The SQLAlchemy model class (e.g., User, Job).
            db:    The active database session (injected).
        """
        self._model = model
        self._db = db

    # ── CREATE ───────────────────────────────────────────────────

    def create(self, obj_data: dict) -> ModelType:
        """
        Insert a new row.

        Args:
            obj_data: Dictionary of column → value mappings.

        Returns:
            The newly created ORM instance with its generated `id`.
        """
        db_obj = self._model(**obj_data)
        self._db.add(db_obj)
        self._db.commit()
        self._db.refresh(db_obj)
        return db_obj

    # ── READ ─────────────────────────────────────────────────────

    def get_by_id(self, obj_id: int) -> Optional[ModelType]:
        """Fetch a single row by primary key. Returns None if not found."""
        return self._db.query(self._model).filter(self._model.id == obj_id).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """
        Fetch multiple rows with pagination.

        Args:
            skip:  Number of rows to skip (OFFSET).
            limit: Maximum rows to return (LIMIT).
        """
        return self._db.query(self._model).offset(skip).limit(limit).all()

    # ── UPDATE ───────────────────────────────────────────────────

    def update(self, obj_id: int, obj_data: dict) -> Optional[ModelType]:
        """
        Update an existing row.

        Only non-None values in `obj_data` are applied, so clients
        can send partial updates (PATCH semantics).

        Returns:
            The updated ORM instance, or None if the row doesn't exist.
        """
        db_obj = self.get_by_id(obj_id)
        if db_obj is None:
            return None

        for key, value in obj_data.items():
            if value is not None:
                setattr(db_obj, key, value)

        self._db.commit()
        self._db.refresh(db_obj)
        return db_obj

    # ── DELETE ───────────────────────────────────────────────────

    def delete(self, obj_id: int) -> bool:
        """
        Delete a row by primary key.

        Returns:
            True if the row existed and was deleted, False otherwise.
        """
        db_obj = self.get_by_id(obj_id)
        if db_obj is None:
            return False

        self._db.delete(db_obj)
        self._db.commit()
        return True
