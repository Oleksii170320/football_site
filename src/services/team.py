from sqlalchemy.orm import Session

from models import team as models, Region
from validation import team as schemas


def get_team(db: Session, team_id: int):
    return db.query(models.Team).filter(models.Team.id == team_id).first()


def get_team_for_slug(db: Session, team_slug: str):
    return db.query(models.Team).filter(models.Team.slug == team_slug).first()


def get_regions_team_list(db: Session, region_slug: str):
    team_list = (
        db.query(models.Team)
        .join(models.Team.region)
        .filter(Region.slug == region_slug)
        .all()
    )
    return team_list


def get_teams(db: Session):
    return db.query(models.Team).all()


def create_team(db: Session, team: schemas.TeamCreateSchemas):
    db_team = models.Team(**team.model_dump())
    db.add(db_team)
    db.commit()
    db.refresh(db_team)
    return db_team


def update_team(db: Session, team_id: int, team: schemas.TeamUpdateSchemas):
    db_team = db.query(models.Team).filter(models.Team.id == team_id).first()
    if db_team is None:
        return None
    for key, value in team.dict().items():
        setattr(db_team, key, value)
    db.commit()
    db.refresh(db_team)
    return db_team


def delete_team(db: Session, team_id: int):
    db_team = db.query(models.Team).filter(models.Team.id == team_id).first()
    if db_team is None:
        return None
    db.delete(db_team)
    db.commit()
    return db_team
