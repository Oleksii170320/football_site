from datetime import date

from sqlalchemy import desc
from sqlalchemy.orm import Session
from models import (
    region as models,
    Season,
    Tournament,
    Organization,
    Region,
)
from validation import region as schemas


def get_region(db: Session, region_slug: str):
    return db.query(models.Region).filter(models.Region.slug == region_slug).first()


def get_regions_list(db: Session, **kwargs):
    """Список всіх регіонів(Областей)"""
    return db.query(Region).all()


def get_regions(db: Session, region_slug: str = None, **kwargs):
    query = db.query(Region).filter(Region.slug == region_slug)
    return query.first()


def get_region_season(db: Session, region_id: int):
    return (
        db.query(Season)
        .join(Season.tournament)
        .join(Tournament.organization)
        .join(Organization.region)
        .filter(Region.id == region_id, Season.year == date.today().year)
        .order_by(desc(Season.year))
        .all()
    )


def get_region_seasons(db: Session, region_id: int):
    return (
        db.query(Season)
        .join(Season.tournament)
        .join(Tournament.organization)
        .join(Organization.region)
        .filter(Region.id == region_id, Season.year == date.today().year)
        .order_by(desc(Season.year))
        .all()
    )


def create_region(db: Session, region: schemas.RegionCreateSchemas):
    db_region = models.Region(**region.model_dump())
    db.add(db_region)
    db.commit()
    db.refresh(db_region)
    return db_region


def update_region(
    db: Session,
    region_id: int,
    # region_name: str,
    region: schemas.RegionUpdateSchemas,
):
    db_region = (
        db.query(models.Region)
        .filter(
            models.Region.id == region_id,
            # models.Region.name == region_name
        )
        .first()
    )
    if db_region is None:
        return None
    for key, value in region.model_dump().items():
        setattr(db_region, key, value)
    db.commit()
    db.refresh(db_region)
    return db_region


def delete_region(db: Session, region_id: int):
    db_region = db.query(models.Region).filter(models.Region.id == region_id).first()
    if db_region is None:
        return None
    db.delete(db_region)
    db.commit()
    return db_region
