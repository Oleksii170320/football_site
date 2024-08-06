from sqlalchemy import desc, or_
from sqlalchemy.orm import Session
from models import match as models
from validation import match as schemas


def get_matches(db: Session):
    return db.query(models.Match).order_by(desc(models.Match.event))


def get_matches_season(db: Session, season_id: int):
    return (
        db.query(models.Match)
        .filter(models.Match.season_id == season_id)
        .order_by(desc(models.Match.event))
    )


def season_matches(db: Session, season_id: int):
    matches = (
        db.query(models.Match).filter(models.Match.season_id == season_id)
    ).order_by(desc(models.Match.event))

    return matches


def get_match(db: Session, match_id: int):
    return db.query(models.Match).filter(models.Match.id == match_id).first()


def get_matches_season(db: Session, season_id: int):
    db_match = db.query(models.Match).filter(models.Match.season_id == season_id).all()
    return db_match


def get_matches_team(db: Session, team_id: int):
    """Всі матчі певної команди"""
    db_match = (
        db.query(models.Match)
        .filter(or_(models.Match.team1_id == team_id, models.Match.team2_id == team_id))
        .order_by(desc(models.Match.event))
        .all()
    )
    return db_match


def get_matches_results_season(db: Session, season_id: int):
    db_match = (
        db.query(models.Match)
        .filter(
            models.Match.season_id == season_id,
            models.Match.status.in_(["played", "technical_defeat"]),
        )
        .order_by(desc(models.Match.event))
        .all()
    )
    return db_match


def get_matches_upcoming_season(db: Session, season_id: int):
    db_match = (
        db.query(models.Match)
        .filter(
            models.Match.season_id == season_id,
            models.Match.status.in_(["not_played", "postponed", "canceled"]),
        )
        .order_by(models.Match.event)
        .all()
    )
    return db_match


def create_match(db: Session, match: schemas.MatchCreateSchemas):
    db_match = models.Match(**match.dict())
    db.add(db_match)
    db.commit()
    db.refresh(db_match)
    return db_match


def update_match(db: Session, match_id: int, match: schemas.MatchUpdateSchemas):
    db_match = db.query(models.Match).filter(models.Match.id == match_id).first()
    if db_match is None:
        return None
    for key, value in match.dict().items():
        setattr(db_match, key, value)
    db.commit()
    db.refresh(db_match)
    return db_match


def delete_match(db: Session, match_id: int):
    db_match = db.query(models.Match).filter(models.Match.id == match_id).first()
    if db_match is None:
        return None
    db.delete(db_match)
    db.commit()
    return db_match
