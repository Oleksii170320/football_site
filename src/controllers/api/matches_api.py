from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from services.matches.match import get_season_all_matches_test

router = APIRouter()


@router.get("/json/matches_in_season/{season_slug}")
async def get_teams_in_season_for_api(season_slug: str, db: AsyncSession = Depends(get_db)):
    """Шукає всі матчі, які грають у розіграші для API"""

    matches = await get_season_all_matches_test(db, season_slug=season_slug)
    if not matches:
        raise HTTPException(status_code=404, detail="Matches not found")
    return matches
