from fastapi import HTTPException
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from models import Region


async def get_regions_list_for_api(db: AsyncSession, **kwargs):
    """Список всіх регіонів(Областей)"""

    result = await db.execute(select(Region))  # Використовуємо select замість query
    regions = result.scalars().all()  # scalars() отримує тільки самі об'єкти без метаданих

    if not regions:
        raise HTTPException(status_code=404, detail="Матчі не знайдено")

    # Перетворюємо результат у список словників
    regions_list = [
        {
            'id': region.id,
            'slug': region.slug,
            'name': region.name,
            'emblem': region.emblem,
            'status': region.status,
        }
        for region in regions
    ]

    # Повертаємо результат у форматі JSON (FastAPI сам це зробить)
    return regions_list
