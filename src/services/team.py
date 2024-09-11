from sqlalchemy import func, case, desc
from sqlalchemy.orm import Session

from models import (
    team as models,
    Region,
    TeamPerson,
    TeamSeason,
    Person,
    PositionRole,
    Position,
    PlayerRole,
    RefEvent,
    MatchProperties,
    MatchEvent,
    Season,
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


def get_teams_in_season(db: Session, season_slug: str):
    team_list = (
        db.query(models.Team)
        .join(TeamSeason, TeamSeason.team_id == models.Team.id)
        .join(Season, Season.id == TeamSeason.season_id)
        .filter(Season.slug == season_slug)
        .order_by(models.Team.name)
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
                    func.strftime("%Y", func.now())
                    - func.strftime("%Y", func.datetime(Person.birthday, "unixepoch"))
                )
                - (
                    func.strftime("%m-%d", func.now())
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
            func.count(func.distinct(MatchProperties.match_id)).label(
                "matches_count"
            ),  # кількість матчів
            func.sum(
                case((RefEvent.id.in_([1, 2]), 1), else_=0)  # Кількість голів
            ).label("goals"),
            func.sum(
                case((RefEvent.id == 2, 1), else_=0)  # Кількість голів з пенальті
            ).label("penalty_goals"),
            func.sum(
                case((RefEvent.id == 5, 1), else_=0)  # Кількість жовтих карток
            ).label("yellow_cards"),
            func.sum(
                case(
                    (RefEvent.id == 6, 1),
                    (RefEvent.id == 7, 1),  # Кількість червоних карток
                    else_=0,
                )
            ).label("red_cards"),
        )
        .join(TeamPerson, TeamPerson.person_id == Person.id)
        .join(PositionRole, PositionRole.team_person_id == TeamPerson.id)
        .join(Position, Position.id == PositionRole.position_id)
        .join(PlayerRole, PlayerRole.id == PositionRole.player_role_id)
        .outerjoin(MatchProperties, MatchProperties.player_id == PositionRole.id)
        .outerjoin(MatchEvent, MatchEvent.player_match_id == MatchProperties.id)
        .outerjoin(RefEvent, RefEvent.id == MatchEvent.event_id)
        .filter(TeamPerson.team_id == team_id, PositionRole.active.is_(True))
        .group_by(
            Person.id,
            Person.photo,
            Person.name,
            Person.surname,
            Person.lastname,
            Position.position,
            PositionRole.position_id,
            PositionRole.player_role_id,
            PositionRole.player_number,
            PlayerRole.full_name,
        )
        .order_by(desc(PositionRole.enddate))
        .all()
    )
    return result


def get_teams(db: Session):
    return db.query(models.Team).order_by(models.Team.name).all()


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


def update_team_logo(db: Session, team_slug: str, new_logo_name: str) -> models.Team:
    # Отримуємо запис команди за ідентифікатором
    team = db.query(models.Team).filter(models.Team.slug == team_slug).first()
    if team is None:
        raise ValueError(f"Команду з id {team_slug} не знайдено.")
    team.logo = new_logo_name
    db.commit()
    db.refresh(team)
    return team


def delete_team(db: Session, team_id: int):
    db_team = db.query(models.Team).filter(models.Team.id == team_id).first()
    if db_team is None:
        return None
    db.delete(db_team)
    db.commit()
    return db_team
