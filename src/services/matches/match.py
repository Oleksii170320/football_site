from datetime import datetime, timedelta

from fastapi import HTTPException
from sqlalchemy import desc, or_, case
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased
from sqlalchemy.sql import func
from sqlalchemy.future import select

from models import (
    Match,
    MatchProperties,
    PositionRole,
    Organization,
    TeamPerson,
    Person,
    Season,
    Tournament,
    Stadium,
    Team,
    Round,
    Stage,
    PlayerRole,
    MatchEvent,
    RefEvent,
    Group,
    Region,
)


async def get_all_match(db: AsyncSession):
    """Асинхронний запит на всі матчі (з необхідними параметрами)"""

    Team1, Team2 = aliased(Team), aliased(Team) # Створюємо аліаси для таблиці Team

    # Побудова асинхронного запиту
    stmt = (
        select(
            Match.id.label("match_id"),
            func.strftime("%d.%m.%Y", func.datetime(Match.event, "unixepoch")).label("event"),
            func.strftime("%H:%M", func.datetime(Match.event, "unixepoch", "localtime")).label("event_time"),
            Match.team1_id.label("team1_id"),
            Match.team2_id.label("team2_id"),
            Match.team1_goals,
            Match.team2_goals,
            Match.team1_penalty,
            Match.team2_penalty,
            Match.status,
            Match.extra_time,
            Season.id.label("season_id"),
            Season.name.label("season_name"),
            Season.year.label("season_year"),
            Season.slug.label("season_slug"),
            Region.name.label("region_name"),
            Region.slug.label("region_slug"),
            Region.emblem.label("region_logo"),
            Region.status.label("region_status"),
            Tournament.logo.label("tournament_logo"),
            Tournament.name.label("tournament_name"),
            Tournament.football_type.label("football_type"),
            Organization.tournament_level.label("tournament_level"),
            Stadium.id.label("stadium_id"),
            Stadium.name.label("stadium_name"),
            Stadium.city.label("stadium_city"),
            Team1.slug.label("team1_slug"),
            Team1.logo.label("team1_logo"),
            Team1.name.label("team1_name"),
            Team1.city.label("team1_city"),
            Team2.slug.label("team2_slug"),
            Team2.name.label("team2_name"),
            Team2.city.label("team2_city"),
            Team2.logo.label("team2_logo"),
            Round.name.label("round_name"),
            Stage.name.label("stage_name"),
            Stage.id.label("stage_id"),
            Group.name.label("group_name"),
        )
        .join(Season, Season.id == Match.season_id)
        .join(Tournament, Tournament.id == Season.tournament_id)
        .join(Organization, Organization.id == Tournament.organization_id)
        .join(Region, Region.id == Organization.region_id)
        .join(Team1, Team1.id == Match.team1_id)
        .join(Team2, Team2.id == Match.team2_id)
        .join(Round, Round.id == Match.round_id)
        .outerjoin(Stage, Stage.id == Match.stage_id)
        .outerjoin(Group, Group.id == Match.group_id)
        .outerjoin(Stadium, Stadium.id == Match.stadium_id)
    )
    return stmt


async def get_matches_all_information(db: AsyncSession):
    """Асинхронний запит всіх матчів"""

    stmt = await get_all_match(db)  # Виклик функції get_all_match з await
    result = await db.execute(stmt)  # Виконання запиту
    return result.all()  # Повернення результатів


async def get_match(db: AsyncSession, match_id: int):
    """Асинхронний запит на певний матч по ІД"""

    stmt = await get_all_match(db)  # Чекаємо, поки отримаємо запит
    stmt = stmt.filter(Match.id == match_id)  # Тепер фільтруємо
    result = await db.execute(stmt)  # Виконуємо запит
    return result.fetchone()  # Повертаємо один рядок


async def get_match_statistics(db: AsyncSession, match_id: int):
    """Асинхронний запит даних статистики матчу (картки, голи і т.д.)"""

    stmt = (
        select(
            MatchProperties.id,
            PositionRole.player_number,
            PlayerRole.name.label("role_name"),
            Person.id.label("player_id"),
            Person.lastname.label("player_lastname"),
            Person.name.label("player_name"),
            MatchProperties.protocol,
            MatchProperties.starting,
            MatchEvent.player_replacement_id,
            case((MatchProperties.end_min - MatchProperties.start_min >0,
                  MatchProperties.end_min - MatchProperties.start_min), else_=0
                 ).label("play_time"),
            TeamPerson.team_id,
            PositionRole.player_role_id,
            func.max(case((RefEvent.id == 10, 1), else_=0)).label("replacement"),          # Для 'replacement' Заміна
            func.sum(case((RefEvent.id.in_([1, 2]), 1), else_=0)).label("all_goals"),      # Для 'all_goals' (рахуємо всі забиті голи)
            func.sum(case((RefEvent.id == 2, 1), else_=0)).label("penalty"),               # Для 'count_penalty' (рахуємо голи з пенальті)
            func.sum(case((RefEvent.id == 4, 1), else_=0)).label("own_goal"),              # Для 'count_own_goal' (рахуємо автоголи)
            func.max(case((RefEvent.id == 5, 1), else_=0)).label("yellow_card"),           # Для 'yellow_card'
            func.max(case((RefEvent.id == 6, 1), else_=0)).label("second_yellow_card"),    # Для 'second_yellow_card'
            func.max(case((RefEvent.id == 7, 1), else_=0)).label("red_card"),              # Для 'red_card'
        )
        .join(MatchProperties, MatchProperties.player_id == PositionRole.id)
        .join(PlayerRole, PlayerRole.id == PositionRole.player_role_id)
        .join(TeamPerson, TeamPerson.id == PositionRole.team_person_id)
        .join(Person, Person.id == TeamPerson.person_id)
        .join(MatchEvent, MatchEvent.player_match_id == MatchProperties.id, isouter=True)
        .join(RefEvent, RefEvent.id == MatchEvent.event_id, isouter=True)
        # .filter(MatchProperties.match_id == match_id)
        .where(MatchProperties.match_id == match_id)
        .group_by(Person.lastname)
    )

    result = await db.execute(stmt)
    return result.fetchall()


# async def get_match_statistics(db: AsyncSession, match_id: int):
#     """Асинхронний запит даних статистики матчу (картки, голи і т.д.)"""
#
#     # Створюємо аліаси для таблиць
#     team_person_alias = aliased(TeamPerson)
#     match_event_alias = aliased(MatchEvent)
#     ref_event_alias = aliased(RefEvent)
#
#     stmt = (
#         select(
#             PositionRole.player_number,
#             PositionRole.player_role_id,
#             PlayerRole.name.label("role_name"),
#             Person.id.label("player_id"),
#             Person.lastname.label("player_lastname"),
#             Person.name.label("player_name"),
#             MatchProperties.protocol,
#             MatchProperties.starting,
#             MatchProperties.start_min.label("from_what_minute"),
#             MatchProperties.end_min.label("how_many_minutes"),
#             MatchProperties.id.label("id_player_in_match"),
#             team_person_alias.team_id,
#             match_event_alias.player_replacement_id,
#             func.max(case((ref_event_alias.id == 10, 1), else_=0)).label("replacement"),        # Для 'replacement' Заміна
#             func.sum(case((ref_event_alias.id.in_([1, 2]), 1), else_=0)).label("all_goals"),    # Для 'all_goals' (рахуємо всі забиті голи)
#             func.sum(case((ref_event_alias.id == 2, 1), else_=0)).label("penalty"),             # Для 'count_penalty' (рахуємо голи з пенальті)
#             func.sum(case((ref_event_alias.id == 4, 1), else_=0)).label("own_goal"),            # Для 'count_own_goal' (рахуємо автоголи)
#             func.max(case((ref_event_alias.id == 5, 1), else_=0)).label("yellow_card"),         # Для 'yellow_card'
#             func.max(case((ref_event_alias.id == 6, 1), else_=0)).label("second_yellow_card" ), # Для 'second_yellow_card'
#             func.max(case((ref_event_alias.id == 7, 1), else_=0)).label("red_card"),            # Для 'red_card'
#         )
#         .join(team_person_alias, team_person_alias.id == MatchProperties.player_id)
#         .join(PositionRole, PositionRole.team_person_id == team_person_alias.id)
#         .join(PlayerRole, PlayerRole.id == PositionRole.player_role_id)
#         .join(Person, Person.id == team_person_alias.person_id)
#         .outerjoin(match_event_alias, match_event_alias.player_match_id == MatchProperties.id)
#         .outerjoin(ref_event_alias, ref_event_alias.id == match_event_alias.event_id)
#         .filter(MatchProperties.match_id == match_id)
#         .group_by(
#             PositionRole.player_number,
#             PositionRole.player_role_id,
#             PlayerRole.name,
#             Person.id,
#             Person.lastname,
#             Person.name,
#             MatchProperties.protocol,
#             MatchProperties.starting,
#             MatchProperties.start_min,
#             MatchProperties.end_min,
#             MatchProperties.id,
#             team_person_alias.team_id,
#             match_event_alias.player_replacement_id,
#         )
#     )
#
#     result = await db.execute(stmt)
#     return result.fetchall()


# async def get_match_event(db: AsyncSession, match_id: int):
#     """Асинхронний запит даних події матчу"""
#
#     stmt = (
#         select(
#             TeamPerson.team_id.label("team_id"),
#             MatchEvent.minute.label("minute"),
#             RefEvent.image.label("event_image"),
#             Person.id.label("person_id"),
#             Person.lastname.label("person_lastname"),
#             Person.name.label("person_name"),
#             MatchEvent.player_replacement_id,
#             RefEvent.name.label("event_name"),
#             MatchEvent.event_id.label("event_id"),
#         )
#         .join(TeamPerson, TeamPerson.person_id == Person.id)
#         .join(PositionRole, PositionRole.team_person_id == TeamPerson.id)
#         .join(MatchProperties, MatchProperties.player_id == PositionRole.id)
#         .join(MatchEvent, MatchEvent.player_match_id == MatchProperties.id)
#         .join(RefEvent, RefEvent.id == MatchEvent.event_id)
#         .filter(MatchProperties.match_id == match_id)
#     )
#
#     result = await db.execute(stmt)
#     return result.all()


async def get_match_event(db: AsyncSession, match_id: int):
    """Асинхронний запит даних події матчу"""

    MatchProperties1 = aliased(MatchProperties)
    MatchProperties2 = aliased(MatchProperties)
    PositionRole1 = aliased(PositionRole)
    PositionRole2 = aliased(PositionRole)
    TeamPerson1 = aliased(TeamPerson)
    TeamPerson2 = aliased(TeamPerson)
    Person1 = aliased(Person)
    Person2 = aliased(Person)

    stmt = (
        select(
            TeamPerson1.team_id.label("team_id"),
            MatchEvent.minute.label("minute"),
            MatchEvent.player_replacement_id,
            MatchEvent.event_id.label("event_id"),
            RefEvent.image.label("event_image"),
            Person1.id.label("person_id"),
            Person1.lastname.label("lastname"),
            Person1.name.label("name"),
            Person2.id.label("replacement_person_id"),
            Person2.lastname.label("replacement_lastname"),
            Person2.name.label("replacement_name"),
        )
        .select_from(MatchProperties1)  # 🔹 Додаємо основну таблицю
        .join(PositionRole1, PositionRole1.id == MatchProperties1.player_id)
        .join(TeamPerson1, TeamPerson1.id == PositionRole1.team_person_id)
        .join(Person1, Person1.id == TeamPerson1.person_id)
        .join(Team, Team.id == TeamPerson1.team_id)
        .outerjoin(MatchEvent, MatchEvent.player_match_id == MatchProperties1.id)
        .join(RefEvent, RefEvent.id == MatchEvent.event_id)
        .outerjoin(MatchProperties2, MatchProperties2.id == MatchEvent.player_replacement_id)
        .outerjoin(PositionRole2, PositionRole2.id == MatchProperties2.player_id)
        .outerjoin(TeamPerson2, TeamPerson2.id == PositionRole2.team_person_id)
        .outerjoin(Person2, Person2.id == TeamPerson2.person_id)
        .filter(MatchProperties1.match_id == match_id)
        .order_by(MatchEvent.minute)
    )

    result = await db.execute(stmt)
    return result.all()


async def get_replacement(db: AsyncSession, match_id: int):
    """Асинхронний запит гравців, які на заміні"""

    stmt = (
        select(
            MatchProperties.id,
            MatchEvent.player_replacement_id
        )
        .join(MatchProperties, MatchProperties.id == MatchEvent.player_replacement_id)
        .filter(
            MatchProperties.match_id == match_id,
            MatchEvent.player_replacement_id.isnot(None),
        )
    )

    result = await db.execute(stmt)
    return result.scalars().all()


async def get_season_all_matches_test(db: AsyncSession, season_slug: str = None):

    """Перелік зіграних матчів поточного розіграшу"""
    Team1, Team2 = aliased(Team), aliased(Team)

    stmt = (
        select(
            Match.id.label("match_id"),
            func.strftime("%d-%m-%Y", func.datetime(Match.event, "unixepoch")).label("event"),
            Match.round_id,
            Round.name.label("round_name"),
            Match.stage_id,
            Stage.name.label("stage_name"),
            Match.group_id,
            Group.name.label("group_name"),
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
            Match.status,
            Season.slug,
        )
        .join(Round, Round.id == Match.round_id)
        .outerjoin(Stage, Stage.id == Match.stage_id)
        .outerjoin(Group, Group.id == Match.group_id)
        .join(Team1, Team1.id == Match.team1_id)
        .join(Team2, Team2.id == Match.team2_id)
        .join(Season, Season.id == Match.season_id)
        .filter(Season.slug == season_slug)
    )

    result = await db.execute(stmt) # Виконуємо запит
    matches = result.fetchall() # Отримуємо всі результати

    if not matches:
        raise HTTPException(status_code=404, detail="Матчі не знайдено")

    # Перетворюємо результат у список словників
    matches_list = [
        {
            "match_id": row.match_id,
            "event": row.event,
            "round_id": row.round_id,
            "round_name": row.round_name,
            "stage_id": row.stage_id,
            "stage_name": row.stage_name,
            "group_id": row.group_id,
            "group_name": row.group_name,
            "team1_id": row.team1_id,
            "team1_slug": row.team1_slug,
            "team1_logo": row.team1_logo,
            "team1_name": row.team1_name,
            "team1_city": row.team1_city,
            "team1_penalty": row.team1_penalty,
            "team1_goals": row.team1_goals,
            "team2_id": row.team2_id,
            "team2_slug": row.team2_slug,
            "team2_logo": row.team2_logo,
            "team2_name": row.team2_name,
            "team2_city": row.team2_city,
            "team2_penalty": row.team2_penalty,
            "team2_goals": row.team2_goals,
            "status": row.status,
            "season_slug": row.slug,
        }
        for row in matches
    ]

    # Повертаємо результат у форматі JSON (FastAPI сам це зробить)
    return matches_list


async def get_region_matches(
        db: AsyncSession,
        region_id: int = None, region_slug: str = None,
        season_id: int = None, season_slug: str = None,
        team_id: int = None, team_slug: str = None,
        # person_id: int = None, person_slug: str = None,
):
    """Перелік всіх матчів поточного регіону"""

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
            Organization.tournament_level
        )
        .join(Season, Season.id == Match.season_id)
        # .join(Person, Person.id == TeamPerson.person_id)
        .join(Tournament, Tournament.id == Season.tournament_id)
        .join(Organization, Organization.id == Tournament.organization_id)
        .join(Region, Region.id == Organization.region_id)
        .join(Team1, Team1.id == Match.team1_id)
        .join(Team2, Team2.id == Match.team2_id)
        .join(Round, Round.id == Match.round_id)
        .outerjoin(Stage, Stage.id == Match.stage_id)
        .outerjoin(Group, Group.id == Match.group_id)
        # .join(MatchProperties, MatchProperties.match_id == Match.id)
        # .join(PositionRole, PositionRole.id == MatchProperties.player_id)
        # .join(TeamPerson, TeamPerson.id == PositionRole.team_person_id)
    )

    if region_id is not None:
        stmt = stmt.filter(Region.id == region_id)
    elif region_slug is not None:
        stmt = stmt.filter(Region.slug == region_slug)
    elif season_id is not None:
        stmt = stmt.filter(Season.id == season_id)
    elif season_slug is not None:
        stmt = stmt.filter(Season.slug == season_slug)
    # elif person_id is not None:
    #     stmt = stmt.filter(Person.id == person_id)
    # elif person_slug is not None:
    #     stmt = stmt.filter(Person.slug == person_slug)
    elif team_id is not None:
        stmt = stmt.filter((Match.team1_id == team_id) | (Match.team2_id == team_id))
    elif team_slug is not None:
        stmt = stmt.filter((Team1.slug == team_slug) | (Team2.slug == team_slug))
    else:
        stmt  # або підняти виключення, якщо обидва параметри None

    return stmt.order_by(Tournament.football_type, Organization.tournament_level)



