from sqlalchemy import desc
from sqlalchemy.orm import Session
from models import (
    News,
    Tournament,
    Region,
    Organization,
)
from validation import match as schemas


def get_news_list(db: Session):
    return db.query(News).order_by(desc(News.event)).all()


def get_news_list_region(db: Session, region_slug: str):
    return (
        db.query(News)
        .join(News.tournament)
        .join(Tournament.organization)
        .join(Organization.region)
        .filter(Region.slug == region_slug)
        .order_by(desc(News.event))
        .all()
    )
