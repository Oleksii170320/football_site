from datetime import datetime, timedelta

from sqlalchemy import desc
from sqlalchemy.ext.asyncio import AsyncSession

from models import Match
from services.matches.match import get_region_matches


async def get_region_matches_week(db: AsyncSession, region_id: int = None, region_slug: str = None):
    """Перелік зіграних матчів поточного розіграшу (+/- 7 днів)"""

    today = datetime.utcnow() # Отримуємо поточний timestamp
    start_date = today - timedelta(days=7) # Обчислюємо межі діапазону
    end_date = today + timedelta(days=7)

    stmt = await get_region_matches(db, region_id=region_id, region_slug=region_slug)

    if stmt is None:
        return []

    stmt = stmt.filter(Match.event.between(start_date.timestamp(), end_date.timestamp()))
    stmt = stmt.order_by(desc(Match.event))

    result = await db.execute(stmt)
    return result.all()
