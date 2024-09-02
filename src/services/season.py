from datetime import datetime

from sqlalchemy import desc, func
from sqlalchemy.orm import Session


from models import (
    Season,
    Team,
    Tournament,
    Organization,
    Region,
)
from validation import season as schemas


def get_season(db: Session, season_id: int):
    return db.query(Season).filter(Season.id == season_id).first()


def get_seasons(db: Session, skip: int = 0, limit: int = 10):
    seasons = (
        db.query(Season).order_by(desc(Season.year)).offset(skip).limit(limit).all()
    )
    return seasons


def get_seasons_years(db: Session):
    """Ця функцыя повертаэ всі діючи на даний момент розіграші"""

    # Отримуємо поточну дату у форматі епохи
    current_epoch = int(datetime.utcnow().timestamp())

    seasons = db.query(Season).filter(Season.end_date >= current_epoch).all()
    return seasons


def get_seasons_tournament(db: Session, tournament_id: int):
    seasons = (
        db.query(Season)
        .join(Season.tournament)
        .filter(Tournament.id == tournament_id)
        .order_by(desc(Season.year))
        .all()
    )
    return seasons


def get_seasons_winner(db: Session, team_id: int):
    """Визначає команду переможча певного розіграшу"""
    seasons = (
        db.query(Season)
        .filter(Season.team_winner_id == team_id)
        .order_by(desc(Season.year))
        .all()
    )
    return seasons


def get_seasons_teams_history(db: Session, team_id: int):
    """Список розіграшів, в яких команда виступала"""
    seasons = (
        db.query(Season)
        .join(Season.teams_associations)
        .filter(Team.id == team_id)
        .order_by(desc(Season.year))
        .all()
    )
    return seasons


def get_season_by_id_or_slug(
    db: Session, season_id: int = None, season_slug: str = None
):
    query = db.query(Season)
    if season_id is not None:
        query = query.filter(Season.id == season_id)
    elif season_slug is not None:
        query = query.filter(Season.slug == season_slug)
    else:
        return None  # or raise an exception if both are None
    return query.first()


def get_season_tournament(db: Session, tournament_id: int):
    """Виводить список сезонів одного турніру по id турніру"""

    season = (
        db.query(Season)
        .filter(Season.tournament_id == tournament_id)
        .order_by(desc(Season.year))
        .all()
    )

    return season


def get_seasons_region(db: Session, region_slug: str):
    current_year = datetime.now().year
    seasons = (
        db.query(
            Region.slug.label("region_slug"),
            Season.id.label("season_id"),
            Season.slug.label("season_slug"),
            Season.name.label("season_name"),
            func.strftime(
                "%Y", func.date(func.datetime(Season.start_date, "unixepoch"))
            ).label("start_date"),
            func.strftime(
                "%Y", func.date(func.datetime(Season.end_date, "unixepoch"))
            ).label("end_date"),
        )
        .join(Tournament, Tournament.id == Season.tournament_id)
        .join(Organization, Organization.id == Tournament.organization_id)
        .join(Region, Region.id == Organization.region_id)
        .filter(
            Region.slug == region_slug,
            func.strftime(
                "%Y", func.date(func.datetime(Season.start_date, "unixepoch"))
            )
            <= str(current_year),
            func.strftime("%Y", func.date(func.datetime(Season.end_date, "unixepoch")))
            >= str(current_year),
        )
        .all()
    )
    return seasons


def get_seasons_region_id(db: Session, region_id: int):
    seasons = (
        db.query(Season)
        .join(Season.tournament)
        .join(Tournament.organization)
        .join(Organization.region)
        .filter(Region.id == region_id)
        .all()
    )
    return seasons


def create_season(db: Session, season: schemas.SeasonCreateSchemas):
    db_season = Season(**season.model_dump())
    db.add(db_season)
    db.commit()
    db.refresh(db_season)
    return db_season


def update_season(db: Session, season_id: int, season: schemas.SeasonUpdateSchemas):
    db_season = db.query(Season).filter(Season.id == season_id).first()
    if db_season is None:
        return None
    for key, value in season.model_dump().items():
        setattr(db_season, key, value)
    db.commit()
    db.refresh(db_season)
    return db_season


def delete_season(db: Session, season_id: int):
    db_season = db.query(Season).filter(Season.id == season_id).first()
    if db_season is None:
        return None
    db.delete(db_season)
    db.commit()
    return db_season


def link_season_team(db: Session, season_id: int, team_id: int):
    season = db.query(Season).filter(Season.id == season_id).first()
    team = db.query(Team).filter(Team.id == team_id).first()
    season.teams_associations.append(team)
    db.commit()
    return season
