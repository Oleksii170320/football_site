from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from models import News, Region, Tournament, Organization


# def get_news_list(db: Session):
#     return db.query(News).order_by(desc(News.event)).all()


async def get_news_list(db: AsyncSession):
    stmt = (
        select(
            News.id,
            News.event,
            func.strftime("%d-%m-%Y", func.datetime(News.event, "unixepoch")).label(
                "date"
            ),
            News.brief,
            News.topic,
            News.photo,
            News.description,
            News.region_id,
            Region.name.label("region_name"),
        )
        .join(Region, Region.id == News.region_id)
        .order_by(desc(News.event))
    )
    result = await db.execute(stmt)
    return result.fetchall()  # Отримуємо всі результати


async def get_news_list_region(db: Session, region_slug: str):
    stmt = (
        select(
            News.id,
            News.event,
            func.strftime("%d-%m-%Y", func.datetime(News.event, "unixepoch")).label(
                "date"
            ),
            News.brief,
            News.topic,
            News.photo,
            News.description,
            News.region_id,
            Region.name.label("region_name"),
        )
        .join(Region, Region.id == News.region_id)
        .filter(Region.slug == region_slug)
        .order_by(desc(News.event))
    )

    result = await db.execute(stmt)
    return result.all()


async def get_news_page(db: AsyncSession, news_id: int):
    stmt = (
        select(
            News.id,
            News.event,
            func.strftime("%d-%m-%Y", func.datetime(News.event, "unixepoch")).label(
                "date"
            ),
            News.brief,
            News.topic,
            News.photo,
            News.description,
            News.region_id,
            Region.name.label("region_name"),
        )
        .join(Region, Region.id == News.region_id)
        .filter(News.id == news_id)
    )

    result = await db.execute(stmt)
    return result.first()
