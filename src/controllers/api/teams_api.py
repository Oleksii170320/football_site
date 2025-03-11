from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from services.teams.team_api import get_all_teams

router = APIRouter()


@router.get("/json/teams_list")
async def get_teams_list(db: AsyncSession = Depends(get_db), team_name: str = None, team_city: str = None, region_name: str = None):
    """API для отримання команд із фільтрацією"""

    teams = await get_all_teams(db, team_name, team_city, region_name)
    if not teams:
        raise HTTPException(status_code=404, detail="Teams not found")

    return teams


@router.get("/json/teams_l")
async def get_teams_in_season_for_api(db: AsyncSession = Depends(get_db)):
    """Шукає всі команди, які грають у розіграші для API"""

    teams = await get_all_teams(db)
    if not teams:
        raise HTTPException(status_code=404, detail="Teams not found")
    return teams


