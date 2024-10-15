from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from core.templating import render
from core.database import get_db
from services.news_list import get_news_page
from services.region import get_regions_list


router = APIRouter()


@router.get("/{news_id}")
async def read_new(request: Request, news_id: int, db: AsyncSession = Depends(get_db)):
    """Виводить дані для конкретної статті новин по ІД"""

    return render(
        "news/news_page.html",
        request,
        {
            "news_page": await get_news_page(db, news_id=news_id),
            "regions_list": await get_regions_list(db),
        },
    )
