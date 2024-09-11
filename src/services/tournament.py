from sqlalchemy import desc
from sqlalchemy.orm import Session
from models import tournament as models, Region, Organization, Season
from validation import tournament as schemas


def get_tournament(db: Session, tournament_id: int):
    return (
        db.query(models.Tournament)
        .filter(models.Tournament.id == tournament_id)
        .first()
    )


# def get_tournament_slug(db: Session, tournament_slug: str):
#     tournaments = (
#         db.query(models.Tournament)
#         .filter(models.Tournament.slug == tournament_slug)
#         .first()
#     )
#     return tournaments


def get_tournament_slug(db: Session, tournament_slug: str):
    return (
        db.query(
            models.Tournament.logo,
            models.Tournament.name,
            models.Tournament.full_name,
            models.Tournament.create_year,
            models.Tournament.level_int,
            models.Tournament.level_up,
            models.Tournament.level_down,
            models.Tournament.website,
            Organization.tournament_level,
            Season.id,
            Season.slug,
            Region.name.label("region_name"),
        )
        .join(Season, Season.tournament_id == models.Tournament.id)
        .join(Organization, Organization.id == models.Tournament.organization_id)
        .join(Region, Region.id == Organization.region_id)
        .filter(models.Tournament.slug == tournament_slug)
        .first()
    )


def get_tournament_for_season(
    db: Session, season_id: int = None, season_slug: str = None, **kwargs
):
    tournaments = (
        db.query(
            models.Tournament.logo,
            models.Tournament.name,
            models.Tournament.full_name,
            models.Tournament.create_year,
            models.Tournament.level_int,
            models.Tournament.level_up,
            models.Tournament.level_down,
            models.Tournament.website,
            Organization.tournament_level,
            Season.id,
            Season.slug,
        )
        .join(Season, Season.tournament_id == models.Tournament.id)
        .join(Organization, Organization.id == models.Tournament.organization_id)
        .filter(Season.slug == season_slug)
        .first()
    )

    return tournaments


def get_tournament_archive(db: Session, tournament_slug: str):
    tournaments = (
        db.query(Season)
        .join(models.Tournament, models.Tournament.id == Season.tournament_id)
        .filter(models.Tournament.slug == tournament_slug)
        .order_by(desc(Season.year))
        .all()
    )
    return tournaments


def get_tournaments(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Tournament).offset(skip).limit(limit).all()


def get_region_tournaments(db: Session, region_slug: str):
    tournaments = (
        db.query(models.Tournament)
        .join(models.Tournament.organization)
        .join(Organization.region)
        .filter(Region.slug == region_slug)
        .all()
    )
    return tournaments


def create_tournament(db: Session, tournament: schemas.TournamentCreateSchemas):
    db_tournament = models.Tournament(**tournament.dict())
    db.add(db_tournament)
    db.commit()
    db.refresh(db_tournament)
    return db_tournament


def update_tournament(
    db: Session, tournament_id: int, tournament: schemas.TournamentUpdateSchemas
):
    db_tournament = (
        db.query(models.Tournament)
        .filter(models.Tournament.id == tournament_id)
        .first()
    )
    if db_tournament is None:
        return None
    for key, value in tournament.dict().items():
        setattr(db_tournament, key, value)
    db.commit()
    db.refresh(db_tournament)
    return db_tournament


def delete_tournament(db: Session, tournament_id: int):
    db_tournament = (
        db.query(models.Tournament)
        .filter(models.Tournament.id == tournament_id)
        .first()
    )
    if db_tournament is None:
        return None
    db.delete(db_tournament)
    db.commit()
    return db_tournament
