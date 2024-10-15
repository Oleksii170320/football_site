from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from services.match import get_season_all_matches_test
from services.team import get_teams_in_season

router = APIRouter()


@router.get("/json/teams_in_season/{season_slug}")
async def get_teams_in_season_endpoint(
    season_slug: str, db: AsyncSession = Depends(get_db)
):
    """Шукає всі команди, які грають у розіграші"""
    teams = await get_teams_in_season(db, season_slug=season_slug)
    if not teams:
        raise HTTPException(status_code=404, detail="Teams not found")
    return teams


@router.get("/json/matches_in_season/{season_slug}")
async def get_teams_in_season_endpoint(
    season_slug: str, db: AsyncSession = Depends(get_db)
):
    """Шукає всі команди, які грають у розіграші"""
    matches = await get_season_all_matches_test(db, season_slug=season_slug)
    if not matches:
        raise HTTPException(status_code=404, detail="Matches not found")
    return matches
