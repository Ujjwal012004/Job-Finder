"""
ORM Models Package.

Imports all models so that `from app.models import ...` works cleanly,
and so that SQLAlchemy's `Base.metadata` discovers every table when
`create_all()` is called.
"""

from app.models.user import User
from app.models.company import Company
from app.models.job import Job
from app.models.application import Application
from app.models.saved_job import SavedJob
from app.models.application_note import ApplicationNote

__all__ = [
    "User",
    "Company",
    "Job",
    "Application",
    "SavedJob",
    "ApplicationNote",
]
