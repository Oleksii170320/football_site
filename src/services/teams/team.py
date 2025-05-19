from typing import Optional

from sqlalchemy import func, case, desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session, aliased, selectinload

from models import (
    Team,
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
    Stadium,
)
from validation import team as schemas


async def get_team(db: AsyncSession, team_id: int = None, team_slug: str = None):
    president = aliased(Person)
    coach = aliased(Person)

    stmt = (
        select(
            Team.id.label("team_id"),
            Team.name.label("team_name"),
            Team.full_name.label("team_full_name"),
            Team.logo.label("team_logo"),
            Team.slug.label("team_slug"),
            Team.foundation_year,
            Team.clubs_site,
            Team.page_facebook,
            Team.page_youtube,
            Team.page_telegram,
            Team.page_instagram,
            Team.president_id,
            president.lastname.label("president_lastname"),
            president.name.label("president_name"),
            president.surname.label("president_surname"),
            Team.coach_id,
            coach.lastname.label("coach_lastname"),
            coach.name.label("coach_name"),
            coach.surname.label("coach_surname"),
            Team.stadium_id,
            Stadium.name.label("stadium_name"),
            Stadium.city.label("stadium_city"),
            Stadium.capacity.label("stadium_capacity"),
        )
        .outerjoin(president, president.id == Team.president_id)
        .outerjoin(coach, coach.id == Team.coach_id)
        .outerjoin(Stadium, Stadium.id == Team.stadium_id)
    )

    if team_id is not None:
        stmt = stmt.filter(Team.id == team_id)
    elif team_slug is not None:
        stmt = stmt.filter(Team.slug == team_slug)
    else:
        return None  # або підняти виключення, якщо обидва параметри None

    result = await db.execute(stmt)
    return result.first()


def get_team_for_slug(db: Session, team_slug: str):
    return db.query(Team).filter(Team.slug == team_slug).first()


async def get_regions_team_list(db: Session, region_slug: str):
    team_list = await db.execute(
        select(Team).join(Team.region).filter(Region.slug == region_slug)
    )
    return team_list.scalars().all()


# async def get_teams_in_season(db: AsyncSession, season_slug: str):
#     stmt = (
#         select(Team)
#         .join(TeamSeason, TeamSeason.team_id == Team.id)
#         .join(Season, Season.id == TeamSeason.season_id)
#         .filter(Season.slug == season_slug)
#         .order_by(Team.name)
#     )
#     result = await db.execute(stmt)
#     team_list = result.scalars().all()
#     return team_list


async def get_teams_for_id(db: AsyncSession, season_id: int):
    # Додайте логування або перевірку даних для відлагодження
    teams = await db.execute(
        select(Team).join(Season.teams_associations).filter(Season.id == season_id)
    )
    return teams.scalars().all()


async def get_team_staff(db: AsyncSession, team_slug: str):
    """Персонал команди"""

    stmt = (
        select(
            Person.id,
            Person.slug,
            Person.photo,
            Person.name,
            Person.surname,
            Person.lastname,
            func.strftime("%d-%m-%Y", func.datetime(Person.birthday, "unixepoch")).label("birthday"),
            func.floor(
                (func.strftime("%Y", func.now()) - func.strftime("%Y", func.datetime(Person.birthday, "unixepoch")))
                - (func.strftime("%m-%d", func.now()) < func.strftime("%m-%d", func.datetime(Person.birthday, "unixepoch")))
            ).label("age"),
            Position.position,
            PositionRole.position_id.label("position_id"),
            PositionRole.player_role_id,
            PositionRole.player_number,
            PlayerRole.full_name,
            func.count(func.distinct(MatchProperties.match_id)).label("matches_count"), # кількість матчів
            func.sum(case((RefEvent.id.in_([1, 2]), 1), else_=0)).label("goals"), # Кількість голів
            func.sum(case((RefEvent.id == 2, 1), else_=0)).label("penalty_goals"), # Кількість голів з пенальті
            func.sum(case((RefEvent.id == 5, 1), else_=0)).label("yellow_cards"),  # Кількість жовтих карток
            func.sum(case((RefEvent.id == 6, 1),(RefEvent.id == 7, 1),else_=0,)).label("red_cards"), # Кількість червоних карток
        )
        .join(TeamPerson, TeamPerson.person_id == Person.id)
        .join(Team, Team.id == TeamPerson.team_id)
        .join(PositionRole, PositionRole.team_person_id == TeamPerson.id)
        .join(Position, Position.id == PositionRole.position_id)
        .join(PlayerRole, PlayerRole.id == PositionRole.player_role_id)
        .outerjoin(MatchProperties, MatchProperties.player_id == PositionRole.id)
        .outerjoin(MatchEvent, MatchEvent.player_match_id == MatchProperties.id)
        .outerjoin(RefEvent, RefEvent.id == MatchEvent.event_id)
        .filter(Team.slug == team_slug, PositionRole.active.is_(True))
        # .filter(TeamPerson.team_id == team_id, PositionRole.active.is_(True))
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
    )

    result = await db.execute(stmt)
    return result.all()


async def get_teams(db: AsyncSession):
    result = await db.execute(select(Team).order_by(Team.name))
    return result.scalars().all()


async def get_team_for_id(db: AsyncSession, team_id: int):
    return await db.get(Team, team_id)


# def create_team(db: Session, team: schemas.TeamCreateSchemas):
#     db_team = Team(**team.model_dump())
#     db.add(db_team)
#     db.commit()
#     db.refresh(db_team)
#     return db_team


# async def create_team(db: AsyncSession, team: schemas.TeamCreateSchemas):
#     db_team = Team(**team.model_dump())
#     db.add(db_team)
#     await db.commit()  # Асинхронний коміт
#     await db.refresh(db_team)  # Оновлення даних
#     return db_team


async def create_team(db: AsyncSession, team: schemas.TeamCreateSchemas):
    db_team = Team(**team.model_dump())
    db.add(db_team)
    await db.commit()
    await db.refresh(db_team)

    # Завантажте асоційовані дані заздалегідь
    await db.execute(
        select(Team)
        .options(
            selectinload(Team.seasons_won),
            selectinload(Team.matches_1),
            selectinload(Team.matches_2),
        )
        .where(Team.id == db_team.id)
    )

    return db_team


async def update_team(
    db: AsyncSession, team_id: int, team: schemas.TeamUpdateSchemas
) -> Optional[Team]:
    async with db.begin():
        # Запит на отримання існуючої команди
        db_team = await db.execute(select(Team).filter(Team.id == team_id))
        db_team = db_team.scalars().first()

        if db_team is None:
            return None

        for key, value in team.dict().items():
            setattr(db_team, key, value)

        db.add(db_team)
        await db.commit()
        return db_team


async def update_team_logo(
    db: AsyncSession, team_slug: str, new_logo_name: str
) -> Optional[Team]:
    async with db.begin():
        # Отримуємо запис команди за slug
        result = await db.execute(select(Team).filter(Team.slug == team_slug))
        team = result.scalars().first()

        if team is None:
            raise ValueError(f"Команду з slug {team_slug} не знайдено.")

        team.logo = new_logo_name
        await db.commit()
        return team


async def delete_team(db: AsyncSession, team_id: int) -> Optional[Team]:
    async with db.begin():
        result = await db.execute(select(Team).filter(Team.id == team_id))
        db_team = result.scalars().first()

        if db_team is None:
            return None

        await db.delete(db_team)
        await db.commit()
        return db_team
