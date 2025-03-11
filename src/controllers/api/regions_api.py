from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from services.regions.region_api import get_regions_list_for_api

router = APIRouter()


@router.get("/json/regions_list")
async def get_all_regions_for_api(db: AsyncSession = Depends(get_db)):
    """Спискок регіонів для API"""

    regions = await get_regions_list_for_api(db)

    if not regions:
        raise HTTPException(status_code=404, detail="Regions not found")
    return regions
