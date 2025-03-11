from datetime import date

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.future import select
from sqlalchemy import desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from models import (
    District,
    Region
)

from validation import district as schemas


async def get_districts_list(db: AsyncSession, region_slug: str):

    """Список всіх районів в даній області"""
    stmt = (
        select(
            District.name,
            District.slug,
            District.emblem
        )
        .join(Region, Region.id == District.region_id)
        .filter(Region.slug == region_slug)
    )

    result = await db.execute(stmt)
    return result.all()

