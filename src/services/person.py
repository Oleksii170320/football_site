from datetime import datetime
from typing import List

from sqlalchemy import desc, extract, and_, func, Integer, case, select, asc
from sqlalchemy.ext.asyncio import AsyncSession
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
    MatchEvent, Round, Stage, Group,
)
from services.matches.match import get_region_matches
from validation import person as schemas


async def get_person(db: AsyncSession, person_id: int):
    """Повна інформація про гравця/персону"""
    current_year = datetime.now().year
    stmt = (
        select(
            Person.id,
            Person.slug,
            Person.photo,
            Person.name,
            Person.lastname,
            Person.surname,
            func.strftime("%d-%m-%Y", func.date(func.datetime(Person.birthday, "unixepoch"))).label("birthday"),
            Person.region_id,
            Region.slug.label("region_slug"),
            Region.name.label("region_name"),
            # Додавання поля для обчислення віку
            (current_year-func.strftime("%Y", func.datetime(Person.birthday, "unixepoch")).cast( Integer)).label("age"),
        )
        .join(Region, Region.id == Person.region_id)
        .filter(Person.id == person_id)
    )

    result = await db.execute(stmt)
    return result.first()


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


async def get_person_matches(db: AsyncSession, person_id: int = None):
    """Команди та періоди, в якіх грав гравець"""

    Team1, Team2 = aliased(Team), aliased(Team)

    stmt = (
        select(
            Match.id.label("match_id"),
            Match.event.label("match_datatime"),
            func.strftime("%d.%m.%Y", func.datetime(Match.event, "unixepoch", "localtime")).label("event"),
            func.strftime("%H:%M", func.datetime(Match.event, "unixepoch", "localtime")).label("event_time"),
            Match.round_id,
            Match.stage_id,
            Match.group_id,
            Match.team1_penalty,
            Match.team1_goals,
            Match.extra_time,
            Match.team2_penalty,
            Match.team2_goals,
            Match.status,
            Match.match_info,
            Match.match_video,
            Team1.id.label("team1_id"),
            Team1.slug.label("team1_slug"),
            Team1.logo.label("team1_logo"),
            Team1.name.label("team1_name"),
            Team1.city.label("team1_city"),
            Team2.id.label("team2_id"),
            Team2.slug.label("team2_slug"),
            Team2.logo.label("team2_logo"),
            Team2.name.label("team2_name"),
            Team2.city.label("team2_city"),
            Round.name.label("round_name"),
            Stage.name.label("stage_name"),
            Group.name.label("group_name"),
            Season.id.label("season_id"),
            Season.slug.label("season_slug"),
            Season.logo.label("season_logo"),
            Season.full_name.label("season_full_name"),
            Season.year.label("season_year"),
            Region.slug.label("region_slug"),
            Region.status.label("region_status"),
            Region.name.label("region_name"),
            Tournament.football_type.label("football_type"),
            Tournament.logo.label("tournament_logo"),
            Person.id.label("person_id"),
        )
        .join(Season, Season.id == Match.season_id)
        .join(Person, Person.id == TeamPerson.person_id)
        .join(Tournament, Tournament.id == Season.tournament_id)
        .join(Organization, Organization.id == Tournament.organization_id)
        .join(Region, Region.id == Organization.region_id)
        .join(Team1, Team1.id == Match.team1_id)
        .join(Team2, Team2.id == Match.team2_id)
        .join(Round, Round.id == Match.round_id)
        .outerjoin(Stage, Stage.id == Match.stage_id)
        .outerjoin(Group, Group.id == Match.group_id)
        .join(MatchProperties, MatchProperties.match_id == Match.id)
        .join(PositionRole, PositionRole.id == MatchProperties.player_id)
        .join(TeamPerson, TeamPerson.id == PositionRole.team_person_id)

        .filter(Person.id == person_id)
        .order_by(desc(Match.event))
    )
    result = await db.execute(stmt)
    return result.all()




async def get_person_team_career(db: AsyncSession, person_id: int):
    """Команди та періоди, в яких грав гравець"""

    stmt = (
        select(
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
    )
    result = await db.execute(stmt)
    return result.all()


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


async def get_person_teams_tournaments(db: AsyncSession, person_id: int):
    """Турніри, в якіх гравець брав участь"""
    stmt = (
        select(
            Team.id.label("team_id"),  # id команди
            Team.slug.label("team_slug"),  # slug команди
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
    )
    result = await db.execute(stmt)
    return result.all()


async def get_region_persons(db: AsyncSession, region_slug: str):
    """Виводить персон, які відносяться до даного регіону"""
    # Створюємо асинхронний запит
    stmt = (
        select(Person)
        .join(Region, Region.id == Person.region_id)
        .filter(Region.slug == region_slug)
    )
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_persons(db: AsyncSession) -> List[Person]:
    result = await db.execute(select(Person))
    return result.scalars().all()


async def create_person(db: AsyncSession, person: schemas.PersonSchemas):
    db_person = Person(**person.dict())
    async with db.begin():  # Запускає асинхронну транзакцію
        db.add(db_person)
        await db.commit()  # Виконує асинхронне збереження
        await db.refresh(db_person)  # Оновлює об'єкт після збереження
    return db_person


async def update_person(
    db: AsyncSession, person_id: int, person: schemas.PersonUpdateSchemas
):
    async with db.begin():  # Запускає асинхронну транзакцію
        db_person = await db.execute(select(Person).filter(Person.id == person_id))
        db_person = db_person.scalars().first()
        if db_person is None:
            return None
        for key, value in person.dict().items():
            setattr(db_person, key, value)
        await db.commit()  # Виконує асинхронне збереження
        await db.refresh(db_person)  # Оновлює об'єкт після збереження
    return db_person


async def delete_person(db: AsyncSession, person_id: int):
    async with db.begin():  # Запускає асинхронну транзакцію
        result = await db.execute(select(Person).filter(Person.id == person_id))
        db_person = result.scalars().first()
        if db_person is None:
            return None
        await db.delete(db_person)  # Виконує асинхронне видалення
        await db.commit()  # Виконує асинхронне збереження
    return db_person
