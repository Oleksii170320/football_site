""" DESCRIPTIONS:
sqlalchemy functions
to get all matches for a team
"""

from sqlalchemy import desc, or_
from sqlalchemy.ext.asyncio import AsyncSession

from models import Match, Team

from services.matches.match import get_all_match, get_region_matches


# async def get_matches_team(db: AsyncSession, team_id: int = None, team_slug: str = None):
#     """Всі матчі певної команди"""
#
#     stmt = await get_all_match(db)
#     stmt = stmt.filter(
#         or_(Match.team1_id == team_id, Match.team2_id == team_id)
#     ).order_by(desc(Match.event))
#
#     result = await db.execute(stmt)
#     return result.all()


async def get_matches_team_results(db: AsyncSession, team_id: int = None, team_slug: str = None):
    """Всі зіграні матчі певної команди"""

    stmt = await get_region_matches(db, team_id=team_id, team_slug=team_slug)

    if stmt is None:
        return []

    stmt = stmt.filter(Match.status.in_(["played", "technical_defeat"]))
    stmt = stmt.order_by(desc(Match.event))

    result = await db.execute(stmt)
    return result.all()


async def get_matches_team_upcoming(db: AsyncSession, team_id: int = None, team_slug: str = None):
    """Всі не зіграні матчі певної команди"""

    stmt = await get_region_matches(db, team_id=team_id, team_slug=team_slug)

    if stmt is None:
        return []

    stmt = stmt.filter(Match.status.in_(["not_played", "postponed", "canceled"]))
    stmt = stmt.order_by(desc(Match.event))

    result = await db.execute(stmt)
    return result.all()
