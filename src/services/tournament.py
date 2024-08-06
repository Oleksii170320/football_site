from sqlalchemy.orm import Session
from models import tournament as models, Region, Organization
from validation import tournament as schemas


def get_tournament(db: Session, tournament_id: int):
    return (
        db.query(models.Tournament)
        .filter(models.Tournament.id == tournament_id)
        .first()
    )


def get_tournament_slug(db: Session, tournament_slug: str):
    tournaments = (
        db.query(models.Tournament)
        .filter(models.Tournament.slug == tournament_slug)
        .first()
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
