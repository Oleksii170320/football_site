from sqlalchemy import desc, func
from sqlalchemy.orm import Session
from models import News, Region, Tournament, Organization


# def get_news_list(db: Session):
#     return db.query(News).order_by(desc(News.event)).all()


def get_news_list(db: Session):
    return (
        db.query(
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
        .all()
    )


def get_news_list_region(db: Session, region_slug: str):
    result = (
        db.query(
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
        .all()
    )
    return result


def get_news_page(db: Session, news_id: int):
    return (
        db.query(
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
        .first()
    )
