from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import Match, Season
from models.stage import Stage


async def get_stages(db: AsyncSession):
    stage_list = await db.execute(select(Stage))
    return stage_list.scalars().all()


async def get_distinct_stages_with_groups(
    db: AsyncSession, season_id: int = None, season_slug: str = None
):
    """Отримує унікальні stage_id з групами для певного сезону асинхронно."""

    stmt = (
        select(Stage.id)
        .join(Match, Match.stage_id == Stage.id)
        .join(Season, Season.id == Match.season_id)
        .distinct()
    )

    if season_id is not None:
        stmt = stmt.filter(Match.season_id == season_id)
    elif season_slug is not None:
        stmt = stmt.filter(Season.slug == season_slug)
    else:
        return None

    result = await db.execute(stmt)
    return result.all()
