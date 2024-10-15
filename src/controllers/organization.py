from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from core.templating import templates, render
from core.database import get_db
from services import organization as crud, get_regions_list
from services.news_list import get_news_list
from validation import organization as schemas


router = APIRouter()


@router.get("/", response_model=List[schemas.OrganizationSchemas])
async def read_organizations(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    """Виводить список всіх футбольних організацій"""

    return render(
        "organizations.html",
        request,
        {
            "news_list": await get_news_list(db),  # Стрічка новин (всі регіони)
            "regions_list": await get_regions_list(db),  # Список регіонів (бокове меню)
            "organizations": await crud.get_organizations(db, skip=skip, limit=limit),
        },
    )


@router.get("/{organization_slug}", response_model=schemas.OrganizationSchemas)
async def read_organization(
    request: Request, organization_slug: str, db: AsyncSession = Depends(get_db)
):
    """Виводить організацію по ІД"""

    return render(
        "organization.html",
        request,
        {
            "news_list": await get_news_list(db),  # Стрічка новин (всі регіони)
            "regions_list": await get_regions_list(db),  # Список регіонів (бокове меню)
            "organization": await crud.get_organization(
                db, organization_slug=organization_slug
            ),
        },
    )


@router.post("/", response_model=schemas.OrganizationSchemas)
async def create_organization(
    organization: schemas.OrganizationCreateSchemas, db: AsyncSession = Depends(get_db)
):
    return await crud.create_organization(db=db, organization=organization)


@router.put("/{organization_id}", response_model=schemas.OrganizationSchemas)
async def update_organization(
    organization_id: int,
    organization: schemas.OrganizationUpdateSchemas,
    db: AsyncSession = Depends(get_db),
):
    db_organization = await crud.update_organization(
        db=db, organization_id=organization_id, organization=organization
    )
    if db_organization is None:
        raise HTTPException(status_code=404, detail="Organization not found")
    return db_organization


@router.delete("/{organization_id}", response_model=schemas.OrganizationSchemas)
async def delete_organization(
    organization_id: int,
    db: AsyncSession = Depends(get_db),
):
    db_organization = await crud.delete_organization(
        db=db, organization_id=organization_id
    )
    if db_organization is None:
        raise HTTPException(status_code=404, detail="Organization not found")
    return db_organization
