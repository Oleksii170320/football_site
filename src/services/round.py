from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.round import Round


async def get_rounds(db: AsyncSession):
    """Список всіх турів/раундів"""

    result = await db.execute(select(Round))
    rounds = result.scalars().all()
    return rounds


async def get_round(db: AsyncSession, round_slug: str):
    result = await db.execute(select(Round).filter(Round.slug == round_slug))
    return result.scalars().first()
