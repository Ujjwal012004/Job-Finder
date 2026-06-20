"""
Application Routes — Apply to jobs, track applications, manage notes.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.application import (
    ApplicationCreate,
    ApplicationUpdate,
    ApplicationResponse,
    SavedJobCreate,
    SavedJobResponse,
    ApplicationNoteCreate,
    ApplicationNoteResponse,
)
from app.repositories.application_repo import ApplicationRepository
from app.repositories.saved_job_repo import SavedJobRepository
from app.repositories.note_repo import ApplicationNoteRepository
from app.auth import get_current_user

router = APIRouter(prefix="/api", tags=["Applications"])


# ── Applications ─────────────────────────────────────────────────

@router.post("/applications", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED)
def create_application(
    app_data: ApplicationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Submit a job application (authenticated)."""
    repo = ApplicationRepository(db)

    # Prevent duplicate applications
    if repo.get_by_user_and_job(current_user.id, app_data.job_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already applied to this job",
        )

    return repo.create({
        "user_id": current_user.id,
        **app_data.model_dump(),
    })


@router.get("/applications", response_model=List[ApplicationResponse])
def list_my_applications(
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List the current user's applications."""
    return ApplicationRepository(db).get_by_user(current_user.id, skip=skip, limit=limit)


@router.get("/applications/{app_id}", response_model=ApplicationResponse)
def get_application(
    app_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a specific application (must belong to the current user)."""
    app = ApplicationRepository(db).get_by_id(app_id)
    if not app or app.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")
    return app


@router.put("/applications/{app_id}", response_model=ApplicationResponse)
def update_application(
    app_id: int,
    update_data: ApplicationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update an application (e.g., change status)."""
    repo = ApplicationRepository(db)
    app = repo.get_by_id(app_id)
    if not app or app.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")

    updated = repo.update(app_id, update_data.model_dump(exclude_unset=True))
    return updated


@router.delete("/applications/{app_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_application(
    app_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Withdraw/delete an application."""
    repo = ApplicationRepository(db)
    app = repo.get_by_id(app_id)
    if not app or app.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")
    repo.delete(app_id)


# ── Saved Jobs (Bookmarks) ──────────────────────────────────────

@router.post("/saved-jobs", response_model=SavedJobResponse, status_code=status.HTTP_201_CREATED)
def save_job(
    data: SavedJobCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Bookmark a job."""
    repo = SavedJobRepository(db)
    if repo.find_bookmark(current_user.id, data.job_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Job already bookmarked",
        )
    return repo.create({"user_id": current_user.id, "job_id": data.job_id})


@router.get("/saved-jobs", response_model=List[SavedJobResponse])
def list_saved_jobs(
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List the current user's bookmarked jobs."""
    return SavedJobRepository(db).get_by_user(current_user.id, skip=skip, limit=limit)


@router.delete("/saved-jobs/{saved_id}", status_code=status.HTTP_204_NO_CONTENT)
def unsave_job(
    saved_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Remove a job bookmark."""
    repo = SavedJobRepository(db)
    saved = repo.get_by_id(saved_id)
    if not saved or saved.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bookmark not found")
    repo.delete(saved_id)


# ── Application Notes ────────────────────────────────────────────

@router.post(
    "/applications/{app_id}/notes",
    response_model=ApplicationNoteResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_note(
    app_id: int,
    note_data: ApplicationNoteCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Add a note to an application."""
    app_repo = ApplicationRepository(db)
    app = app_repo.get_by_id(app_id)
    if not app or app.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")

    return ApplicationNoteRepository(db).create({
        "application_id": app_id,
        **note_data.model_dump(),
    })


@router.get("/applications/{app_id}/notes", response_model=List[ApplicationNoteResponse])
def list_notes(
    app_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all notes for an application."""
    app_repo = ApplicationRepository(db)
    app = app_repo.get_by_id(app_id)
    if not app or app.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")

    return ApplicationNoteRepository(db).get_by_application(app_id)
