""" DESCRIPTIONS:
sqlalchemy functions
to get the "Draw Matches" data of a specific tournament
"""

from datetime import datetime, timedelta

from sqlalchemy import desc, asc
from sqlalchemy.ext.asyncio import AsyncSession

from models import Match, Round
from services.matches.match import get_region_matches


async def get_season_matches_week(db: AsyncSession, season_id: int = None, season_slug: str = None):
    """Перелік зіграних матчів поточного розіграшу (+/- 7 днів)"""

    today = datetime.utcnow() # Отримуємо поточний timestamp
    start_date = today - timedelta(days=7) # Обчислюємо межі діапазону
    end_date = today + timedelta(days=7)

    stmt = await get_region_matches(db, season_id=season_id, season_slug=season_slug)

    if stmt is None:
        return []

    stmt = stmt.filter(Match.event.between(start_date.timestamp(), end_date.timestamp()))
    stmt = stmt.order_by(desc(Match.event))

    result = await db.execute(stmt)
    return result.all()


async def get_season_matches_results(db: AsyncSession, season_id: int = None, season_slug: str = None):
    """Перелік зіграних матчів поточного розіграшу"""

    stmt = await get_region_matches(db, season_id=season_id, season_slug=season_slug)

    if stmt is None:
        return []

    stmt = stmt.filter(Match.status.in_(["played", "technical_defeat"]))
    stmt = stmt.order_by(desc(Match.round_id), asc(Match.event))

    result = await db.execute(stmt)
    return result.all()


async def get_season_matches_upcoming(db: AsyncSession, season_id: int = None, season_slug: str = None):
    """Перелік майбутніх матчів поточного розіграшу"""

    stmt = await get_region_matches(db, season_id=season_id, season_slug=season_slug)

    if stmt is None:
        return []

    stmt = stmt.filter(Match.status.in_(["not_played", "postponed", "canceled"]))
    stmt = stmt.order_by(
        asc(Round.id),
        asc(Match.event),
    )

    result = await db.execute(stmt)
    return result.all()


async def get_season_all_matches(db: AsyncSession, season_id: int = None, season_slug: str = None):
    """Перелік всіх календарних матчів поточного розіграшу, для редагування"""

    stmt = await get_region_matches(db, season_id=season_id, season_slug=season_slug)

    if stmt is None:
        return []

    stmt = stmt.order_by(asc(Match.event))
    result = await db.execute(stmt)
    return result.all()
