from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from models import stadium as models, Team
from validation import stadium as schemas


async def get_stadium(db: AsyncSession, stadium_id: int):
    stmt = select(models.Stadium).filter(models.Stadium.id == stadium_id)
    result = await db.execute(stmt)
    return result.scalars().first()


async def get_stadium_teams(db: AsyncSession, stadium_id: int):
    """Запит для визначення домашнього стадіону певної команди"""

    stmt = (
        select(
            models.Stadium.id,
            Team.slug,
            Team.name,
            Team.city,
        )
        .join(Team, Team.stadium_id == models.Stadium.id)
        .filter(models.Stadium.id == stadium_id)
    )

    result = await db.execute(stmt)
    return result.all()


async def get_stadiums(db: AsyncSession, skip: int = 0, limit: int = 100):
    """Запит на всі стадіони в БД з урахуванням падінгу"""
    stmt = select(models.Stadium).offset(skip).limit(limit)

    async with db.execute(stmt) as result:
        stadiums = result.all()

    return stadiums


async def get_all_stadiums(db: AsyncSession):
    stmt = await db.execute(select(models.Stadium))
    return stmt.scalars().all()


async def get_search_stadiums(db: AsyncSession, query: str):
    """Пошук стадіонів за введеним запитом"""
    stmt = select(
        models.Stadium.id,
        models.Stadium.name,
        models.Stadium.city,
        models.Stadium.address,
        models.Stadium.photo,
        models.Stadium.capacity,
        models.Stadium.dimensions,
        models.Stadium.type_coverage,
        models.Stadium.region_id,
    ).filter(
        or_(
            models.Stadium.name.ilike(f"%{query}%"),
            models.Stadium.city.ilike(f"%{query}%"),
        )
    )

    async with db.execute(stmt) as result:
        stadiums = result.fetchall()

    return stadiums


async def create_stadium(db: AsyncSession, stadium: schemas.StadiumCreateSchemas):
    db_stadium = models.Stadium(**stadium.dict())
    async with db.begin():  # Використовуйте асинхронний контекст менеджера
        db.add(db_stadium)
        await db.commit()
        await db.refresh(db_stadium)
    return db_stadium


async def update_stadium(
    db: AsyncSession, stadium_id: int, stadium: schemas.StadiumUpdateSchemas
):
    async with db.begin():  # Використовуємо асинхронний контекст менеджер
        query = select(models.Stadium).filter(models.Stadium.id == stadium_id)
        result = await db.execute(query)
        db_stadium = result.scalars().first()

        if db_stadium is None:
            return None

        for key, value in stadium.dict().items():
            setattr(db_stadium, key, value)

        await db.commit()
        return db_stadium


async def delete_stadium(db: AsyncSession, stadium_id: int):
    async with db.begin():
        query = select(models.Stadium).filter(models.Stadium.id == stadium_id)
        result = await db.execute(query)
        db_stadium = result.scalars().first()

        if db_stadium is None:
            return None

        delete_query = delete(models.Stadium).where(models.Stadium.id == stadium_id)
        await db.execute(delete_query)
        await db.commit()
        return db_stadium
