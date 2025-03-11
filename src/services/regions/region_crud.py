from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from models import Region
from validation import region as schemas


async def create_region(db: AsyncSession, region: schemas.RegionCreateSchemas):
    db_region = Region(**region.model_dump())
    db.add(db_region)
    await db.commit()  # Асинхронний коміт
    await db.refresh(db_region)  # Асинхронне оновлення об'єкта після вставки
    return db_region


async def update_region(db: AsyncSession, region_id: int, region: schemas.RegionUpdateSchemas):

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
    db_region = db.query(Region).filter(Region.id == region_id).first()
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
