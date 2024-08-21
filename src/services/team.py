from sqlalchemy import func
from sqlalchemy.orm import Session

from models import (
    team as models,
    Region,
    TeamPerson,
    Person,
    PositionRole,
    Position,
    PlayerRole,
)
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


def get_team_staff(db: Session, team_id: int):
    """Персонал команди"""

    result = (
        db.query(
            Person.id,
            Person.photo,
            Person.name,
            Person.surname,
            Person.lastname,
            func.strftime(
                "%d-%m-%Y", func.datetime(Person.birthday, "unixepoch")
            ).label("birthday"),
            func.floor(
                (
                    func.strftime("%Y", "now")
                    - func.strftime("%Y", func.datetime(Person.birthday, "unixepoch"))
                )
                - (
                    func.strftime("%m-%d", "now")
                    < func.strftime(
                        "%m-%d", func.datetime(Person.birthday, "unixepoch")
                    )
                )
            ).label("age"),
            Position.position,
            PositionRole.position_id.label("position_id"),
            PositionRole.player_role_id,
            PositionRole.player_number,
            PlayerRole.full_name,
        )
        .join(TeamPerson, TeamPerson.person_id == Person.id)
        .join(PositionRole, PositionRole.team_person_id == TeamPerson.id)
        .join(Position, Position.id == PositionRole.position_id)
        .join(PlayerRole, PlayerRole.id == PositionRole.player_role_id)
        .filter(TeamPerson.team_id == team_id, PositionRole.active.is_(True))
        .all()
    )
    return result


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
