from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from models import Season, Match, Stage
from models.group import Group


async def get_groups(db: AsyncSession):
    """Отримати всі групи асинхронно."""

    result = await db.execute(select(Group))
    return result.scalars().all()


# async def get_group_in_season(
#     db: AsyncSession, season_id: int = None, season_slug: str = None
# ):
#     """Отримати групи для певного сезону."""
#
#     stmt = (
#         select(Group.id, Group.name, Match.stage_id, Stage.name.label("stage_name"))
#         .join(Season, Season.id == Group.season_id)
#         .join(Match, Match.group_id == Group.id)
#         .join(Stage, Stage.id == Match.stage_id)
#         .group_by(Group.name)
#     )
#
#     if season_id is not None:
#         stmt = stmt.filter(Group.season_id == season_id)
#     elif season_slug is not None:
#         stmt = stmt.filter(Season.slug == season_slug)
#     else:
#         return []  # або підняти виключення, якщо обидва параметри None
#
#     result = await db.execute(stmt)
#     return result.all()


async def get_group_in_season(
    db: AsyncSession, season_id: int = None, season_slug: str = None
):
    """Отримати групи для певного сезону."""

    stmt = (
        select(
            Group.id,
            Group.name,
            Match.stage_id,
            Stage.name.label("stage_name")
        )
        .join(Group, Group.id == Match.group_id)
        .join(Season, Season.id == Match.season_id)
        .join(Stage, Stage.id == Match.stage_id)
        .group_by(Group.name)
    )

    if season_id is not None:
        stmt = stmt.filter(Season.season_id == season_id)
    elif season_slug is not None:
        stmt = stmt.filter(Season.slug == season_slug)
    else:
        return []  # або підняти виключення, якщо обидва параметри None

    result = await db.execute(stmt)
    return result.all()
