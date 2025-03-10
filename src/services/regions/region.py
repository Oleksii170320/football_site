from datetime import date

from sqlalchemy.future import select
from sqlalchemy import desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from models import (
    Season,
    Tournament,
    Organization,
    Region,
)


async def get_region(db: AsyncSession, region_slug: str):
    result = await db.execute(select(Region).filter(Region.slug == region_slug))
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
