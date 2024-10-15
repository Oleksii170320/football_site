from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import desc, or_, func, case, select, asc, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session, aliased
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
from validation import match as schemas


async def get_all_match(db: AsyncSession):
    """Асинхронний запит на всі матчі (з необхідними параметрами)"""

    # Створюємо аліаси для таблиці Team
    team1_alias = aliased(Team)
    team2_alias = aliased(Team)

    # Побудова асинхронного запиту
    stmt = (
        select(
            Match.id.label("match_id"),
            func.strftime("%d-%m-%Y", func.datetime(Match.event, "unixepoch")).label(
                "event"
            ),
            Match.team1_id.label("team1_id"),
            Match.team2_id.label("team2_id"),
            Season.id.label("season_id"),
            Season.name.label("season_name"),
            Season.year.label("season_year"),
            Season.slug.label("season_slug"),
            Region.slug.label("region_slug"),
            Tournament.logo.label("tournament_logo"),
            Tournament.name.label("tournament_name"),
            Stadium.id.label("stadium_id"),
            Stadium.name.label("stadium_name"),
            Stadium.city.label("stadium_city"),
            team1_alias.slug.label("team1_slug"),
            team1_alias.logo.label("team1_logo"),
            team1_alias.name.label("team1_name"),
            team1_alias.city.label("team1_city"),
            Match.team1_goals,
            Match.team2_goals,
            Match.team1_penalty,
            Match.team2_penalty,
            team2_alias.slug.label("team2_slug"),
            team2_alias.name.label("team2_name"),
            team2_alias.city.label("team2_city"),
            team2_alias.logo.label("team2_logo"),
            Match.status,
            Round.name.label("round_name"),
            Stage.name.label("stage_name"),
            Group.name.label("group_name"),
        )
        .join(Season, Season.id == Match.season_id)
        .join(Tournament, Tournament.id == Season.tournament_id)
        .join(Organization, Organization.id == Tournament.organization_id)
        .join(Region, Region.id == Organization.region_id)
        .outerjoin(Stadium, Stadium.id == Match.stadium_id)
        .join(team1_alias, team1_alias.id == Match.team1_id)
        .join(team2_alias, team2_alias.id == Match.team2_id)
        .join(Round, Round.id == Match.round_id)
        .outerjoin(Stage, Stage.id == Match.stage_id)
        .outerjoin(Group, Group.id == Match.group_id)
    )

    return stmt


async def get_matches(db: AsyncSession):
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


async def get_matches_team(db: AsyncSession, team_id: int):
    """Всі матчі певної команди"""

    stmt = await get_all_match(db)

    stmt = stmt.filter(
        or_(Match.team1_id == team_id, Match.team2_id == team_id)
    ).order_by(desc(Match.event))

    result = await db.execute(stmt)
    return result.all()


async def get_match_statistics(db: AsyncSession, match_id: int):
    """Асинхронний запит даних статистики матчу (картки, голи і т.д.)"""

    # Створюємо аліаси для таблиць
    team_person_alias = aliased(TeamPerson)
    match_event_alias = aliased(MatchEvent)
    ref_event_alias = aliased(RefEvent)

    stmt = (
        select(
            PositionRole.player_number,
            PositionRole.player_role_id,
            PlayerRole.name.label("role_name"),
            Person.id.label("player_id"),
            Person.lastname.label("player_lastname"),
            Person.name.label("player_name"),
            MatchProperties.protocol,
            MatchProperties.starting,
            MatchProperties.start_min.label("from_what_minute"),
            MatchProperties.end_min.label("how_many_minutes"),
            MatchProperties.id.label("id_player_in_match"),
            team_person_alias.team_id,
            match_event_alias.player_replacement_id,
            # Для 'replacement'
            func.max(case((ref_event_alias.id == 10, 1), else_=0)).label("replacement"),
            # Для 'all_goals' (рахуємо всі забиті голи)
            func.sum(case((ref_event_alias.id.in_([1, 2]), 1), else_=0)).label(
                "all_goals"
            ),
            # Для 'count_penalty' (рахуємо голи з пенальті)
            func.sum(case((ref_event_alias.id == 2, 1), else_=0)).label("penalty"),
            # Для 'count_own_goal' (рахуємо автоголи)
            func.sum(case((ref_event_alias.id == 4, 1), else_=0)).label("own_goal"),
            # Для 'yellow_card'
            func.max(case((ref_event_alias.id == 5, 1), else_=0)).label("yellow_card"),
            # Для 'second_yellow_card'
            func.max(case((ref_event_alias.id == 6, 1), else_=0)).label(
                "second_yellow_card"
            ),
            # Для 'red_card'
            func.max(case((ref_event_alias.id == 7, 1), else_=0)).label("red_card"),
        )
        .join(team_person_alias, team_person_alias.id == MatchProperties.player_id)
        .join(PositionRole, PositionRole.team_person_id == team_person_alias.id)
        .join(PlayerRole, PlayerRole.id == PositionRole.player_role_id)
        .join(Person, Person.id == team_person_alias.person_id)
        .outerjoin(
            match_event_alias, match_event_alias.player_match_id == MatchProperties.id
        )
        .outerjoin(ref_event_alias, ref_event_alias.id == match_event_alias.event_id)
        .filter(MatchProperties.match_id == match_id)
        .group_by(
            PositionRole.player_number,
            PositionRole.player_role_id,
            PlayerRole.name,
            Person.id,
            Person.lastname,
            Person.name,
            MatchProperties.protocol,
            MatchProperties.starting,
            MatchProperties.start_min,
            MatchProperties.end_min,
            MatchProperties.id,
            team_person_alias.team_id,
            match_event_alias.player_replacement_id,
        )
    )

    result = await db.execute(stmt)
    return result.fetchall()


async def get_match_event(db: AsyncSession, match_id: int):
    """Асинхронний запит даних події матчу"""

    stmt = (
        select(
            Person.id.label("person_id"),
            Person.name.label("person_name"),
            Person.lastname.label("person_lastname"),
            RefEvent.name.label("event_name"),
            RefEvent.image.label("event_image"),
            MatchEvent.minute.label("minute"),
            MatchEvent.event_id.label("event_id"),
            MatchEvent.player_replacement_id,
            TeamPerson.team_id.label("team_id"),
        )
        .join(TeamPerson, TeamPerson.person_id == Person.id)
        .join(PositionRole, PositionRole.team_person_id == TeamPerson.id)
        .join(MatchProperties, MatchProperties.player_id == PositionRole.id)
        .join(MatchEvent, MatchEvent.player_match_id == MatchProperties.id)
        .join(RefEvent, RefEvent.id == MatchEvent.event_id)
        .filter(MatchProperties.match_id == match_id)
    )

    result = await db.execute(stmt)
    return result.all()


async def get_match_replacement(db: AsyncSession, match_id: int):
    """Асинхронний запит всіх зроблених замін в матчі"""

    # Гравці, яких замінили
    subquery = (
        select(MatchEvent.player_replacement_id)
        .join(MatchProperties, MatchProperties.id == MatchEvent.player_match_id)
        .filter(
            MatchProperties.match_id == match_id,
            MatchEvent.player_replacement_id.isnot(None),
        )
        .subquery()
    )

    # Основний запит, що використовує підзапит
    stmt = (
        select(
            Person.id.label("person_id"),
            Person.name.label("person_name"),
            Person.lastname.label("person_lastname"),
            MatchProperties.player_id.label("player_id"),
            MatchProperties.id.label("player_match_id"),
        )
        .join(TeamPerson, TeamPerson.id == MatchProperties.player_id)
        .join(Person, Person.id == TeamPerson.person_id)
        .filter(MatchProperties.id.in_(subquery))
    )

    result = await db.execute(stmt)
    return result.all()


async def get_replacement(db: AsyncSession, match_id: int):
    """Асинхронний запит гравців, які на заміні"""

    stmt = (
        select(MatchEvent.player_replacement_id)
        .join(MatchProperties, MatchProperties.id == MatchEvent.player_match_id)
        .filter(
            MatchProperties.match_id == match_id,
            MatchEvent.player_replacement_id.isnot(None),
        )
    )

    result = await db.execute(stmt)
    return result.scalars().all()


def get_matches_season(db: Session, season_id: int):
    """Запит вміх матсів данного розіграшу"""

    return (
        db.query(Match).filter(Match.season_id == season_id).order_by(desc(Match.event))
    )


def sdc(db: Session, season_id: int):
    """Запит вміх матсів данного розіграшу"""

    matches = (db.query(Match).filter(Match.season_id == season_id)).order_by(
        desc(Match.event)
    )

    return matches


def get_matches_season(db: Session, season_id: int):
    db_match = db.query(Match).filter(Match.season_id == season_id).all()
    return db_match


def get_matches_round(db: Session, season_id: int):
    db_match = (
        db.query(Round.id, Round.name)
        .join(Round, Round.id == Match.round_id)
        .filter(Match.season_id == season_id)
        .group_by(Round.id)  # Використовуємо distinct без аргументів
        .all()
    )
    return db_match


def get_matches_results_season(db: Session, season_id: int):
    db_match = (
        db.query(Match)
        .filter(
            Match.season_id == season_id,
            Match.status.in_(["played", "technical_defeat"]),
        )
        .order_by(desc(Match.event))
        .all()
    )
    return db_match


async def get_season_matches(
    db: AsyncSession, season_id: int = None, season_slug: str = None
):
    """Перелік всіх матчів поточного розіграшу"""
    Team1 = aliased(Team)
    Team2 = aliased(Team)

    stmt = (
        select(
            Match.id.label("match_id"),
            func.strftime("%d-%m-%Y", func.datetime(Match.event, "unixepoch")).label(
                "event"
            ),
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
    )

    if season_id is not None:
        stmt = stmt.filter(Match.season_id == season_id)
    elif season_slug is not None:
        stmt = stmt.filter(Season.slug == season_slug)
    else:
        return None  # або підняти виключення, якщо обидва параметри None

    return stmt


async def get_season_matches_weeks(
    db: AsyncSession, season_id: int = None, season_slug: str = None
):
    """Перелік матчів поточного розіграшу в межах -7 до +7 днів від поточної дати"""
    # Обчислення дати -7 та +7 днів від поточної дати
    current_date = datetime.now()
    start_date = current_date - timedelta(days=7)
    end_date = current_date + timedelta(days=7)

    # Отримання базового запиту матчів
    stmt = await get_season_matches(db, season_id=season_id, season_slug=season_slug)

    if stmt is None:
        return []

    # Додаткове фільтрування за діапазоном дат
    stmt = stmt.filter(
        func.date(Match.event, "unixepoch").between(
            start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")
        )
    )

    result = await db.execute(stmt)
    return result.all()


async def get_season_all_matches(
    db: AsyncSession, season_id: int = None, season_slug: str = None
):
    """Перелік зіграних матчів поточного розіграшу"""

    stmt = await get_season_matches(db, season_id=season_id, season_slug=season_slug)

    if stmt is None:
        return []

    stmt = stmt.order_by(desc(Match.event))

    result = await db.execute(stmt)
    return result.all()


from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import aliased
from sqlalchemy.sql import func
from models import Match, Team, Round, Stage, Group, Season
import json


async def get_season_all_matches_test(db: AsyncSession, season_slug: str = None):
    """Перелік зіграних матчів поточного розіграшу"""
    Team1 = aliased(Team)
    Team2 = aliased(Team)

    stmt = (
        select(
            Match.id.label("match_id"),
            func.strftime("%d-%m-%Y", func.datetime(Match.event, "unixepoch")).label(
                "event"
            ),
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

    # Виконуємо запит
    result = await db.execute(stmt)

    # Отримуємо всі результати
    matches = result.fetchall()

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


async def get_season_matches_results(
    db: AsyncSession, season_id: int = None, season_slug: str = None
):
    """Перелік зіграних матчів поточного розіграшу"""

    stmt = await get_season_matches(db, season_id=season_id, season_slug=season_slug)

    if stmt is None:
        return []

    stmt = stmt.filter(Match.status.in_(["played", "technical_defeat"]))
    stmt = stmt.order_by(desc(Match.event))

    result = await db.execute(stmt)
    return result.all()


async def get_season_matches_upcoming(
    db: AsyncSession, season_id: int = None, season_slug: str = None
):
    """Перелік не зіграних матчів поточного розіграшу"""

    stmt = await get_season_matches(db, season_id=season_id, season_slug=season_slug)

    if stmt is None:
        return []

    stmt = stmt.filter(Match.status.in_(["not_played", "postponed", "canceled"]))
    stmt = stmt.order_by(
        asc(Round.id),
        asc(Match.event),
    )

    result = await db.execute(stmt)
    return result.all()


def get_season_matches_schedule(
    db: Session, season_id: int = None, season_slug: str = None
):
    """Перелік не зіграних матчів поточного розіграшу"""
    matches_upcoming = (
        get_season_matches(db, season_id=season_id, season_slug=season_slug)
        .order_by(Round.id)  # Сортування в зворотному порядку
        .all()
    )
    return matches_upcoming


async def create_match(db: AsyncSession, match: schemas.MatchCreateSchemas):
    new_match = Match(**match.dict())
    db.add(new_match)
    await db.commit()
    await db.refresh(new_match)
    return new_match


def update_match(db: Session, match_id: int, match: schemas.MatchUpdateSchemas):
    db_match = db.query(Match).filter(Match.id == match_id).first()
    if db_match is None:
        return None
    for key, value in match.dict().items():
        setattr(db_match, key, value)
    db.commit()
    db.refresh(db_match)
    return db_match


async def update_match(
    db: AsyncSession, match_id: int, match: schemas.MatchUpdateSchemas
) -> Optional[schemas.MatchSchemas]:
    async with db.begin():  # Запускає транзакцію
        query = (
            update(Match)
            .where(Match.id == match_id)
            .values(
                # Вставте всі поля, які потрібно оновити, з match
                team1=match.team1,
                team2=match.team2,
                date=match.date,
                # додайте інші поля
            )
            .returning(Match)
        )
        result = await db.execute(query)
        updated_match = result.scalars().first()
        if updated_match is None:
            return None
        return updated_match


async def delete_match(
    db: AsyncSession, match_id: int
) -> Optional[schemas.MatchSchemas]:
    async with db.begin():  # Запускає транзакцію

        query = select(Match).where(Match.id == match_id)
        result = await db.execute(query)
        db_match = result.scalars().first()

        if db_match is None:
            return None

        query = delete(Match).where(Match.id == match_id)
        await db.execute(query)
        return db_match
