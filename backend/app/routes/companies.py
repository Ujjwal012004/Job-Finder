"""
Company Routes — CRUD for companies.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.company import CompanyCreate, CompanyUpdate, CompanyResponse
from app.repositories.company_repo import CompanyRepository

router = APIRouter(prefix="/api/companies", tags=["Companies"])


@router.post("/", response_model=CompanyResponse, status_code=status.HTTP_201_CREATED)
def create_company(company_data: CompanyCreate, db: Session = Depends(get_db)):
    """Create a new company entry."""
    repo = CompanyRepository(db)
    if repo.find_by_name(company_data.name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Company with this name already exists",
        )
    return repo.create(company_data.model_dump())


@router.get("/", response_model=List[CompanyResponse])
def list_companies(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    """List all companies with pagination."""
    return CompanyRepository(db).get_all(skip=skip, limit=limit)


@router.get("/{company_id}", response_model=CompanyResponse)
def get_company(company_id: int, db: Session = Depends(get_db)):
    """Get a single company by ID."""
    company = CompanyRepository(db).get_by_id(company_id)
    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
    return company


@router.put("/{company_id}", response_model=CompanyResponse)
def update_company(company_id: int, update_data: CompanyUpdate, db: Session = Depends(get_db)):
    """Update a company."""
    updated = CompanyRepository(db).update(company_id, update_data.model_dump(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
    return updated


@router.delete("/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_company(company_id: int, db: Session = Depends(get_db)):
    """Delete a company and all its associated jobs (cascade)."""
    if not CompanyRepository(db).delete(company_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
