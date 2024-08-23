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
            News.category_id,
            Tournament.name.label("tournament_name"),
        )
        .join(Tournament, Tournament.id == News.category_id)
        .join(Organization, Organization.id == Tournament.organization_id)
        .join(Region, Region.id == Organization.region_id)
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
            News.category_id,
            Tournament.name.label("tournament_name"),
        )
        .join(Tournament, Tournament.id == News.category_id)
        .join(Organization, Organization.id == Tournament.organization_id)
        .join(Region, Region.id == Organization.region_id)
        .filter(Region.slug == region_slug)
        .order_by(desc(News.event))
        .all()
    )
    return result
