"""
Database engine, session factory, and base model.

This module is the single source of truth for database connectivity.
All ORM models inherit from `Base`, and all request handlers receive
a scoped session via the `get_db()` dependency.

Key OOP Concept — Dependency Injection:
    FastAPI routes don't create their own DB sessions. Instead, they
    declare a dependency on `get_db()`, which yields a session and
    guarantees cleanup. This inverts the control: the framework
    manages the resource lifecycle, not the consumer.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.config import settings

# --------------------------------------------------------------------------
# Engine
# --------------------------------------------------------------------------
# `connect_args` is needed only for SQLite to allow multi-threaded access.
# For PostgreSQL in production, remove it.
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    echo=settings.DEBUG,       # Log all SQL when in debug mode
    pool_pre_ping=True,        # Verify connections before reuse
)

# --------------------------------------------------------------------------
# Session Factory
# --------------------------------------------------------------------------
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# --------------------------------------------------------------------------
# Declarative Base
# --------------------------------------------------------------------------
# Every ORM model class inherits from this Base.
# It provides the metaclass machinery that maps Python classes → DB tables.
Base = declarative_base()


# --------------------------------------------------------------------------
# Dependency — yields a DB session per request
# --------------------------------------------------------------------------
def get_db():
    """
    FastAPI dependency that provides a database session.

    Usage in a route:
        @router.get("/items")
        def list_items(db: Session = Depends(get_db)):
            ...

    The `yield` keyword makes this a generator-based dependency.
    The `finally` block guarantees the session is closed even if
    the route handler raises an exception — this prevents connection leaks.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
