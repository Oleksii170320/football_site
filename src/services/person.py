from datetime import datetime

from sqlalchemy import desc, extract, and_, func, Integer, case
from sqlalchemy.orm import Session, aliased

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
    PlayerRole,
    MatchProperties,
    Match,
    RefEvent,
    MatchEvent,
)
from validation import person as schemas


def get_person(db: Session, person_id: int):
    """Повна інформація про гравця/персону"""
    current_year = datetime.now().year
    result = (
        db.query(
            Person.id,
            Person.slug,
            Person.photo,
            Person.name,
            Person.lastname,
            Person.surname,
            func.strftime(
                "%d-%m-%Y", func.date(func.datetime(Person.birthday, "unixepoch"))
            ).label("birthday"),
            Person.region_id,
            Region.slug.label("region_slug"),
            Region.name.label("region_name"),
            # Додавання поля для обчислення віку
            (
                current_year
                - func.strftime("%Y", func.datetime(Person.birthday, "unixepoch")).cast(
                    Integer
                )
            ).label("age"),
        )
        .join(Region, Region.id == Person.region_id)
        .filter(Person.id == person_id)
        .first()
    )
    return result


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
            PositionRole.player_role_id,
            PlayerRole.full_name,
            PositionRole.strong_leg,
        )
        .join(Region, Region.id == Person.region_id)
        .join(TeamPerson, TeamPerson.person_id == Person.id)
        .join(Team, Team.id == TeamPerson.team_id)
        .join(PositionRole, PositionRole.team_person_id == TeamPerson.id)
        .join(Position, Position.id == PositionRole.position_id)
        .join(PlayerRole, PlayerRole.id == PositionRole.player_role_id)
        .filter(Person.id == person_id, PositionRole.enddate.is_(None))
        .all()
    )


def get_person_matches(db: Session, person_id: int):
    """Команди та періоди, в якіх грав гравець"""

    Team1 = aliased(Team)
    Team2 = aliased(Team)

    result = (
        db.query(
            Person.id.label("person_id"),
            Match.id.label("match_id"),
            func.strftime("%d-%m-%Y", func.datetime(Match.event, "unixepoch")).label(
                "event"
            ),
            Team1.id.label("team1_id"),
            Team1.slug.label("team1_slug"),
            Team1.logo.label("team1_logo"),
            Team1.name.label("team1_name"),
            Team1.city.label("team1_city"),
            Match.team1_penalty,
            Match.team1_goals,
            Match.team2_penalty,
            Match.team2_goals,
            Team2.id.label("team2_id"),
            Team2.slug.label("team2_slug"),
            Team2.logo.label("team2_logo"),
            Team2.name.label("team2_name"),
            Team2.city.label("team2_city"),
            Season.name.label("season_name"),
            Season.year.label("season_year"),
        )
        .join(Team1, Team1.id == Match.team1_id)
        .join(Team2, Team2.id == Match.team2_id)
        .join(MatchProperties, MatchProperties.match_id == Match.id)
        .join(PositionRole, PositionRole.id == MatchProperties.player_id)
        .join(TeamPerson, TeamPerson.id == PositionRole.team_person_id)
        .join(Person, Person.id == TeamPerson.person_id)
        .join(Season, Season.id == Match.season_id)
        .filter(Person.id == person_id)
        .order_by(desc(Match.event))
        .all()
    )
    return result


def get_person_team_career(db: Session, person_id: int):
    """Команди та періоди, в яких грав гравець"""

    result = (
        db.query(
            PositionRole.player_number.label("player_number"),  # Номер футболки гравця
            Team.id.label("team_id"),  # id команди
            Team.slug.label("team_slug"),
            Team.logo.label("team_logo"),  # логотип команди
            Team.name.label("team_name"),  # Назва команди
            Team.city.label("team_city"),  # Місто команди
            Position.position.label("position"),  # Позиція гравця
            func.strftime(
                "%Y", func.date(func.datetime(PositionRole.startdate, "unixepoch"))
            ).label("startdate"),
            func.strftime(
                "%Y", func.date(func.datetime(PositionRole.enddate, "unixepoch"))
            ).label("enddate"),
            func.count(func.distinct(MatchProperties.match_id)).label(
                "matches_count"
            ),  # кількість матчів
            func.sum(case((RefEvent.id == 1, 1), (RefEvent.id == 2, 1), else_=0)).label(
                "goals"
            ),  # Кількість голів
            func.sum(case((RefEvent.id == 2, 1), else_=0)).label(
                "penalty_goals"
            ),  # Кількість голів з пенальті
            func.sum(case((RefEvent.id == 5, 1), else_=0)).label(
                "yellow_cards"
            ),  # Кількість жовтих карток
            func.sum(case((RefEvent.id == 6, 1), (RefEvent.id == 7, 1), else_=0)).label(
                "red_cards"
            ),  # Кількість червоних карток
        )
        .join(TeamPerson, PositionRole.team_person_id == TeamPerson.id)
        .join(Team, TeamPerson.team_id == Team.id)
        .join(Position, Position.id == PositionRole.position_id)
        .outerjoin(MatchProperties, MatchProperties.player_id == PositionRole.id)
        .outerjoin(MatchEvent, MatchEvent.player_match_id == MatchProperties.id)
        .outerjoin(RefEvent, RefEvent.id == MatchEvent.event_id)
        .filter(TeamPerson.person_id == person_id)
        .group_by(
            Team.id,
            Team.slug,
            Team.logo,
            Team.name,
            Team.city,
            Position.position,
            PositionRole.player_number,
            PositionRole.startdate,
            PositionRole.enddate,
        )
        .order_by(desc(PositionRole.enddate))
        .all()
    )
    return result


# def get_person_team_career(db: Session, person_id: int):
#     """Команди та періоди, в якіх грав гравець"""
#
#     result = (
#         db.query(
#             Team.id,  # id команди
#             PositionRole.player_number,  # номер футболки гравця в даній команді
#             Team.logo,  # логотип команди
#             Team.name,  # Назва команди
#             Team.city,  # Місто команди
#             func.strftime(
#                 "%Y", func.date(func.datetime(PositionRole.startdate, "unixepoch"))
#             ).label("startdate"),
#             func.strftime(
#                 "%Y", func.date(func.datetime(PositionRole.enddate, "unixepoch"))
#             ).label("enddate"),
#             Position.position,  # Дата персони в команді
#             func.strftime("%Y", func.now()).label("current_year"),
#         )
#         .join(TeamPerson, PositionRole.team_person_id == TeamPerson.id)
#         .join(Team, TeamPerson.team_id == Team.id)
#         .join(Position, Position.id == PositionRole.position_id)
#         .filter(TeamPerson.person_id == person_id)
#         .order_by(desc(PositionRole.enddate))
#         .all()
#     )
#     return result


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


def get_region_persons(db: Session, region_slug: str):
    """Виводить персон, які відносяться до даного регіону"""
    persons_list = (
        db.query(Person)
        .join(Region, Region.id == Person.region_id)
        .filter(Region.slug == region_slug)
        .all()
    )
    return persons_list


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
