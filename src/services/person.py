from datetime import datetime

from sqlalchemy import desc, extract, and_, func
from sqlalchemy.orm import Session

from models import (
    Person,
    TeamPerson,
    Team,
    PositionRole,
    Region,
    Position,
    TeamSeason,
    Season,
    Tournament,
    Organization,
    Association,
    Region,
)
from validation import person as schemas


def get_person(db: Session, person_id: int):
    return db.query(Person).filter(Person.id == person_id).first()


def get_person_team(db: Session, person_id: int):
    return (
        db.query(
            Person.id,
            Person.name,
            Person.surname,
            Person.lastname,
            Person.birthday,
            Region.name.label("region_name"),
            Team.id.label("team_id"),
            Team.name.label("team_name"),
            Team.city.label("team_city"),
            Position.position,
            PositionRole.type_role,
            PositionRole.strong_leg,
        )
        .join(Region, Region.id == Person.region_id)
        .join(TeamPerson, TeamPerson.person_id == Person.id)
        .join(Team, Team.id == TeamPerson.team_id)
        .join(PositionRole, PositionRole.team_person_id == TeamPerson.id)
        .join(Position, Position.id == PositionRole.position_id)
        .filter(Person.id == person_id, PositionRole.enddate.is_(None))
        .all()
    )


def get_person_team_career(db: Session, person_id: int):
    """Команди та періоди, в якіх грав гравець"""

    result = (
        db.query(
            Team.id,  # id команди
            PositionRole.player_number,  # номер футболки гравця в даній команді
            Team.logo,  # логотип команди
            Team.name,  # Назва команди
            Team.city,  # Місто команди
            # PositionRole.startdate,  # Дата заявки гравця в команді
            # PositionRole.enddate,  # Дата відзаявки гравцяя в команді
            func.strftime(
                "%Y", func.date(func.datetime(PositionRole.startdate, "unixepoch"))
            ).label("startdate"),
            func.strftime(
                "%Y", func.date(func.datetime(PositionRole.enddate, "unixepoch"))
            ).label("enddate"),
            Position.position,  # Дата персони в команді
            func.strftime("%Y", func.now()).label("current_year"),
        )
        .join(TeamPerson, PositionRole.team_person_id == TeamPerson.id)
        .join(Team, TeamPerson.team_id == Team.id)
        .join(Position, Position.id == PositionRole.position_id)
        .filter(TeamPerson.person_id == person_id)
        .order_by(desc(PositionRole.enddate))
        .all()
    )
    return result


def get_person_teams_tournaments(db: Session, person_id: int):
    """Турніри, в якіх гравець брав участь"""
    result = (
        db.query(
            Team.id.label("team_id"),  # id команди
            Team.logo.label("team_logo"),  # логотип команди
            Team.name.label("team_name"),  # Назва команди
            Team.city.label("team_city"),  # Місто команди
            Association.name.label("association_name"),  # Коротка назва асоціації
            Organization.name.label("organization_name"),  # Коротка назва  федерації
            Organization.tournament_level.label(
                "level"
            ),  # Рівень в структурі федерації
            Season.year.label("season_year"),  # рік розіграшу
            Season.name.label("season_name"),  # назва турніру в рамках даного розіграшу
            Season.slug.label("season_slug"),  # слаг даного розіграшу
            Region.slug.label("region_slug"),  # слаг регіону
            Tournament.id.label("tournament_id"),  # id турніру
            PositionRole.startdate.label("start_date"),  # Додавання дати заявки гравця
            PositionRole.enddate.label("end_date"),  # Додавання дати відзаявки гравця
            func.strftime(
                "%Y", func.date(func.datetime(PositionRole.startdate, "unixepoch"))
            ).label("year_1"),
            func.strftime(
                "%Y", func.date(func.datetime(PositionRole.enddate, "unixepoch"))
            ).label("year_2"),
        )
        .join(TeamPerson, TeamPerson.id == PositionRole.team_person_id)
        .join(Team, Team.id == TeamPerson.team_id)
        .join(TeamSeason, TeamSeason.team_id == Team.id)
        .join(Season, Season.id == TeamSeason.season_id)
        .join(Tournament, Tournament.id == Season.tournament_id)
        .join(Organization, Organization.id == Tournament.organization_id)
        .join(Region, Region.id == Organization.region_id)
        .join(Association, Association.id == Organization.association_id)
        .filter(TeamPerson.person_id == person_id)
        .filter(
            and_(
                PositionRole.startdate <= Season.start_date,
                PositionRole.enddate >= Season.start_date,
            )
        )
        .order_by(Season.year.desc())
        .all()
    )
    return result


def get_persons(db: Session):
    persons_list = db.query(Person).all()
    return persons_list


def create_person(db: Session, person: schemas.PersonSchemas):
    db_person = Person(**person.dict())
    db.add(db_person)
    db.commit()
    db.refresh(db_person)
    return db_person


def update_person(db: Session, person_id: int, person: schemas.PersonUpdateSchemas):
    db_person = db.query(Person).filter(Person.id == person_id).first()
    if db_person is None:
        return None
    for key, value in person.dict().items():
        setattr(db_person, key, value)
    db.commit()
    db.refresh(db_person)
    return db_person


def delete_person(db: Session, person_id: int):
    db_person = db.query(Person).filter(Person.id == person_id).first()
    if db_person is None:
        return None
    db.delete(db_person)
    db.commit()
    return db_person
