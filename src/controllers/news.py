from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from typing import List

from core.templating import templates
from core.database import get_db
from services.news_list import get_news_page
from services.region import get_regions_list

from validation import news as schemas

router = APIRouter()


@router.get("/{news_id}", response_model=List[schemas.NewsTableSchemas])
def read_new(request: Request, news_id: int, db: Session = Depends(get_db)):
    """Виводить дані для конкретної статті новин по ІД"""

    regions_list = get_regions_list(db)
    news_page = get_news_page(db, news_id=news_id)

    return templates.TemplateResponse(
        "news/news_page.html",
        {
            "request": request,
            "news_page": news_page,  # Стрічка новин (всі регіони)
            "regions_list": regions_list,  # Список регіонів (бокове меню)
        },
    )
