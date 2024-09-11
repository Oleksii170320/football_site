from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List

from core.templating import templates
from core.database import get_db
from services import organization as crud
from validation import organization as schemas


router = APIRouter()


@router.get("/", response_model=List[schemas.OrganizationSchemas])
def read_organizations(
    request: Request, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    """Виводить список всіх футбольних організацій"""

    organizations = crud.get_organizations(db, skip=skip, limit=limit)
    return templates.TemplateResponse(
        "organizations.html",
        {
            "request": request,
            "organizations": organizations,
        },
    )


@router.get("/{organization_id}", response_model=schemas.OrganizationSchemas)
def read_organization(
    request: Request, organization_id: int, db: Session = Depends(get_db)
):
    """Виводить огранізацію по ІД"""

    organization = crud.get_organization(db, organization_id=organization_id)
    if organization is None:
        raise HTTPException(status_code=404, detail="Organization not found")
    return templates.TemplateResponse(
        "organization.html",
        {
            "request": request,
            "organization": organization,
        },
    )


@router.post("/", response_model=schemas.OrganizationSchemas)
def create_organization(
    organization: schemas.OrganizationCreateSchemas, db: Session = Depends(get_db)
):
    return crud.create_organization(db=db, organization=organization)


@router.put("/{organization_id}", response_model=schemas.OrganizationSchemas)
def update_organization(
    organization_id: int,
    organization: schemas.OrganizationUpdateSchemas,
    db: Session = Depends(get_db),
):
    db_organization = crud.update_organization(
        db=db, organization_id=organization_id, organization=organization
    )
    if db_organization is None:
        raise HTTPException(status_code=404, detail="Organization not found")
    return db_organization


@router.delete("/{organization_id}", response_model=schemas.OrganizationSchemas)
def delete_organization(organization_id: int, db: Session = Depends(get_db)):
    db_organization = crud.delete_organization(db=db, organization_id=organization_id)
    if db_organization is None:
        raise HTTPException(status_code=404, detail="Organization not found")
    return db_organization
