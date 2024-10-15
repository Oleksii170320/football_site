from http.client import HTTPException
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from models import Region
from models.organization import Organization
from validation import organization as schemas


async def get_organizations(
    db: AsyncSession, skip: int = 0, limit: int = 100
) -> List[schemas.OrganizationSchemas]:
    stmt = select(Organization).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_organization(
    db: AsyncSession, organization_slug: str
) -> Optional[Organization]:
    stmt = select(Organization).filter(Organization.slug == organization_slug)
    result = await db.execute(stmt)
    return result.scalars().first()


async def get_region_organization(db: Session, region_slug: str):
    stmt = (
        select(
            Region.id.label("region_id"),
            Organization.id.label("organization_id"),
            Organization.slug,
            Organization.logo,
            Organization.name,
            Organization.full_name,
            Organization.description,
            Organization.website,
            Organization.tournament_level,
        )
        .join(Organization, Organization.region_id == Region.id)
        .filter(Region.slug == region_slug)
    )
    result = await db.execute(stmt)
    return result.all()


async def create_organization(
    db: AsyncSession, organization: schemas.OrganizationCreateSchemas
) -> Organization:
    db_organization = Organization(**organization.dict())
    async with db.begin():  # Запускає транзакцію
        db.add(db_organization)
        try:
            await db.commit()
            await db.refresh(db_organization)  # Оновлює екземпляр після коміту
        except IntegrityError:
            await db.rollback()  # Откатує транзакцію у разі помилки
            raise HTTPException(
                status_code=400, detail="Organization could not be created."
            )
    return db_organization


async def update_organization(
    db: AsyncSession,
    organization_id: int,
    organization: schemas.OrganizationUpdateSchemas,
) -> Optional[Organization]:
    async with db.begin():  # Запускає транзакцію
        # Шукає організацію за ID
        result = await db.execute(
            select(Organization).filter(Organization.id == organization_id)
        )
        db_organization = result.scalar_one_or_none()

        if db_organization is None:
            return None

        # Оновлює атрибути організації
        for key, value in organization.dict().items():
            setattr(db_organization, key, value)

        try:
            await db.commit()
            await db.refresh(db_organization)  # Оновлює об'єкт після коміту
        except Exception as e:
            await db.rollback()  # Откатує транзакцію у разі помилки
            raise HTTPException(
                status_code=400, detail="Failed to update organization."
            )

    return db_organization


async def delete_organization(
    db: AsyncSession, organization_id: int
) -> Optional[Organization]:
    async with db.begin():  # Запускає транзакцію
        # Шукає організацію за ID
        result = await db.execute(
            select(Organization).filter(Organization.id == organization_id)
        )
        db_organization = result.scalar_one_or_none()

        if db_organization is None:
            return None

        try:
            await db.delete(db_organization)
            await db.commit()  # Асинхронно комітить зміни
        except Exception as e:
            await db.rollback()  # Откатує транзакцію у разі помилки
            raise HTTPException(
                status_code=400, detail="Failed to delete organization."
            )

    return db_organization
