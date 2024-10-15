from datetime import date

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.future import select
from sqlalchemy import desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from models import (
    region as models,
    Season,
    Tournament,
    Organization,
    Region,
)
from validation import region as schemas


async def get_region(db: AsyncSession, region_slug: str):
    result = await db.execute(select(Region).filter(models.Region.slug == region_slug))
    return result.scalars().first()


async def get_regions_list(db: AsyncSession, **kwargs):
    """Список всіх регіонів(Областей)"""
    result = await db.execute(select(Region))  # Використовуємо select замість query
    return result.scalars().all()  # scalars() отримує тільки самі об'єкти без метаданих


async def get_regions(db: AsyncSession, region_slug: str = None, **kwargs):
    query = await db.execute(
        select(
            Region.id,
            Region.slug,
            Region.emblem,
            Region.name,
        ).filter(Region.slug == region_slug)
    )
    return query.first()


async def get_region_season(db: AsyncSession, region_id: int):
    stmt = (
        select(Season)
        .join(Season.tournament)
        .join(Tournament.organization)
        .join(Organization.region)
        .filter(Region.id == region_id, Season.year == date.today().year)
        .order_by(desc(Season.year))
    )
    result = await db.execute(stmt)  # Асинхронне виконання запиту
    return result.scalars().all()  # Отримуємо всі результати


async def get_region_seasons(db: Session, region_id: int):
    stmt = (
        select(Season)
        .join(Season.tournament)
        .join(Tournament.organization)
        .join(Organization.region)
        .filter(Region.id == region_id, Season.year == date.today().year)
        .order_by(desc(Season.year))
    )
    result = await db.execute(stmt)
    return result.scalars().all()


async def create_region(db: AsyncSession, region: schemas.RegionCreateSchemas):
    db_region = models.Region(**region.model_dump())
    db.add(db_region)
    await db.commit()  # Асинхронний коміт
    await db.refresh(db_region)  # Асинхронне оновлення об'єкта після вставки
    return db_region


async def update_region(
    db: AsyncSession, region_id: int, region: schemas.RegionUpdateSchemas
):
    result = await db.execute(select(Region).where(Region.id == region_id))
    db_region = result.scalar_one_or_none()

    if db_region is None:
        return None

    for key, value in region.dict(exclude_unset=True).items():
        setattr(db_region, key, value)

    await db.commit()
    await db.refresh(db_region)
    return db_region


async def delete_region(db: Session, region_id: int):
    db_region = db.query(models.Region).filter(models.Region.id == region_id).first()
    if db_region is None:
        return None
    db.delete(db_region)
    db.commit()
    return db_region


async def delete_region(db: AsyncSession, region_id: int):
    result = await db.execute(select(Region).where(Region.id == region_id))
    db_region = result.scalar_one_or_none()

    if db_region is None:
        return None

    await db.delete(db_region)
    await db.commit()
    return db_region
