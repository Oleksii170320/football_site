from datetime import datetime

from fastapi import HTTPException
from sqlalchemy import desc, func, select, and_, or_
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session, selectinload


from models import (
    Season,
    Team,
    Tournament,
    Organization,
    Association,
    Region,
    TeamSeason,
)
from validation import season as schemas
from validation.team import TeamSchemas


async def get_seasons(db: AsyncSession, skip: int = 0, limit: int = 10):
    stmt = select(Season).order_by(desc(Season.year)).offset(skip).limit(limit)
    result = await db.execute(stmt)
    seasons = result.scalars().all()
    return seasons


async def get_season(db: AsyncSession, season_slug: str):
    result = await db.execute(select(Season).filter(Season.slug == season_slug))
    return result.scalars().first()


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


async def get_seasons_winner(db: AsyncSession, team_slug: str):
    """Визначає команду переможця певного розіграшу"""

    stmt = (
        select(
            Season.slug.label("season_slug"),
            Season.name.label("season_name"),
            Season.full_name.label("season_full_name"),
            Season.year.label("season_year"),
            Season.logo.label("season_logo"),
            Region.slug.label("region_slug"),
            Tournament.logo.label("tournament_logo"),
        )
        .join(Team, Team.id == Season.team_winner_id)
        .join(Tournament, Tournament.id == Season.tournament_id)
        .join(Organization, Organization.id == Tournament.organization_id)
        .join(Region, Region.id == Organization.region_id)
        .filter(Team.slug == team_slug)
        .order_by(desc(Season.year))
    )

    result = await db.execute(stmt)
    return result.all()


async def get_seasons_teams_history(db: AsyncSession, team_slug: str):
    """Список розіграшів, в яких команда виступала"""
    stmt = (
        select(
            Season.slug.label("season_slug"),
            Season.name.label("season_name"),
            Season.full_name.label("season_full_name"),
            Season.logo.label("season_logo"),
            Season.year.label("season_year"),
            Region.slug.label("region_slug"),
            Association.name.label("association_name"),
            Organization.name.label("organization_name"),
            Tournament.logo.label("tournament_logo"),
        )
        .join(TeamSeason, TeamSeason.season_id == Season.id)
        .join(Team, Team.id == TeamSeason.team_id)
        .join(Tournament, Tournament.id == Season.tournament_id)
        .join(Organization, Organization.id == Tournament.organization_id)
        .join(Association, Association.id == Organization.association_id)
        .join(Region, Region.id == Organization.region_id)
        .filter(Team.slug == team_slug)
        .order_by(desc(Season.year))
    )

    result = await db.execute(stmt)
    return result.all()


async def get_season_for_id(db: AsyncSession, season_id: int):
    return await db.get(Season, season_id)


async def get_season_by_id_or_slug(db: AsyncSession, season_id: int = None, season_slug: str = None, **kwargs):
    """Отримує сезон за ідентифікатором або slug (асинхронно)"""

    stmt = (select(
        Season.id.label("season_id"),
        Season.slug.label("season_slug"),
        Season.name.label("season_name"),
        Season.full_name.label("full_name"),
        Season.year.label("season_year"),
        Season.logo.label("season_logo"),
        func.strftime("%d.%m.%Y", func.datetime(Season.start_date, "unixepoch", "localtime")).label("start_date"),
        func.strftime("%d.%m.%Y", func.datetime(Season.end_date, "unixepoch", "localtime")).label("end_date"),
        Season.standing,
        Season.team_winner_id.label("season_winner_id"),
        Tournament.full_name.label("tournament_full_name"),
        Tournament.slug.label("tournament_slug"),
        Tournament.logo.label("tournament_logo"),
        Tournament.level_int.label("tournament_level_int"),
        Tournament.level.label("tournament_level"),
        Tournament.level_up.label("tournament_level_up"),
        Tournament.level_down.label("tournament_level_down"),
        Tournament.website.label("tournament_website"),
        Tournament.description.label("tournament_description"),
        Tournament.football_type.label("football_type"),
        Tournament.page_youtube.label("page_youtube"),
        Tournament.page_facebook.label("page_facebook"),
        Tournament.page_instagram.label("page_instagram"),
        Tournament.page_telegram.label("page_telegram"),
        Organization.tournament_level.label("organization_level"),
        Organization.name.label("organization_name"),
        Organization.slug.label("organization_slug"),
        Region.name.label("region_name"),
        Region.slug.label("region_slug"),
        Region.status.label("region_status"),
        Team.name.label("season_winner_name"),
        Team.city.label("season_winner_city"),
        Team.slug.label("season_winner_slug"),
        Team.logo.label("season_winner_logo"),
    )
        .join(Tournament, Tournament.id == Season.tournament_id)
        .join(Organization, Organization.id == Tournament.organization_id)
        .join(Region, Organization.region_id == Region.id)
        .outerjoin(Team, Team.id == Season.team_winner_id)
    )

    if season_id is not None:
        stmt = stmt.filter(Season.id == season_id)
    elif season_slug is not None:
        stmt = stmt.filter(Season.slug == season_slug)
    else:
        return None  # або викликати виключення, якщо обидва параметри None

    result = await db.execute(stmt)
    return result.first()


async def get_season_previous_winner(db: AsyncSession, season_id: int = None, season_slug: str = None, **kwargs):
    """Отримати попереднього переможця розіграшу"""

    # Отримуємо tournament_id та start_date для поточного сезону
    tournament_query = (
        select(Season.tournament_id, Season.start_date)
        .filter(or_(Season.id == season_id, Season.slug == season_slug))
        .limit(1)
    )

    tournament_result = await db.execute(tournament_query)
    tournament_data = tournament_result.first()

    if not tournament_data:
        return None  # Якщо не знайшли турнір, повертаємо None

    tournament_id, current_start_date = tournament_data

    # Отримуємо id поточного сезону
    current_season_query = (
        select(Season.id)
        .filter(and_(
            Season.tournament_id == tournament_id,
            or_(Season.id == season_id, Season.slug == season_slug),
        ))
        .limit(1)
    )

    current_season_result = await db.execute(current_season_query)
    current_season_id = current_season_result.scalar()

    if not current_season_id:
        return None

    # Основний запит для пошуку попереднього переможця
    stmt = (
        select(
            Season.id.label("season_id"),
            Season.team_winner_id.label("season_winner_id"),
            Season.year.label("season_year"),
            Team.name.label("season_winner_name"),
            Team.city.label("season_winner_city"),
            Team.slug.label("season_winner_slug"),
            Team.logo.label("season_winner_logo"),
        )
        .join(Team, Team.id == Season.team_winner_id)
        .filter(
            and_(
                Season.tournament_id == tournament_id,  # Фільтр по турніру
                Season.team_winner_id.isnot(None),  # Тільки сезони з переможцем
                Season.id != current_season_id,  # Виключаємо поточний сезон
                Season.end_date < current_start_date,  # Тільки попередні сезони
            )
        )
        .order_by(desc(Season.end_date))  # Останній завершений сезон
        .limit(1)
    )

    result = await db.execute(stmt)
    return result.first()


async def link_season_team(db: AsyncSession, season_id: int, team_id: int):
    """Прив'язує команду до сезону."""
    # Отримати сезон з бази даних
    season = await db.get(Season, season_id)

    if not season:
        raise HTTPException(status_code=404, detail="Season not found")

    # Отримати команду з бази даних
    team = await db.get(Team, team_id)

    if not team:
        raise HTTPException(status_code=404, detail="Team not found")


    season.teams.append(team)  # Додайте команду до списку команд сезону

    # Збережіть зміни в базі даних
    await db.commit()

    # Перетворення команди на словник для Pydantic
    team_data = team.to_dict()  # Використання методу to_dict()

    # Використання Pydantic для створення TeamSchemas
    team_schema = TeamSchemas.from_orm(team_data)

    return team_schema


async def get_seasons_region(db: AsyncSession, region_slug: str, season_slug: str = None, **kwargs):

    current_year = datetime.now().year

    stmt = (
        select(
            Region.slug.label("region_slug"),
            Region.emblem.label("region_logo"),
            Season.id.label("season_id"),
            Season.slug.label("season_slug"),
            Season.name.label("season_name"),
            Season.full_name.label("season_full_name"),
            func.strftime("%Y", func.date(func.datetime(Season.start_date, "unixepoch"))).label("start_date"),
            func.strftime("%Y", func.date(func.datetime(Season.end_date, "unixepoch"))).label("end_date"),
            Tournament.football_type.label("football_type"),
            Tournament.slug.label("tournament_slug"),
            Organization.tournament_level.label("tournament_level"),
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
        .order_by(Tournament.level_int, desc(Season.end_date))
    )

    result = await db.execute(stmt)
    return result.all()


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


async def create_season(db: AsyncSession, season: schemas.SeasonCreateSchemas):

    db_season = Season(**season.dict())
    async with db.begin():
        db.add(db_season)
        await db.flush()
    await db.refresh(db_season)
    return db_season


async def update_season( db: AsyncSession, season_id: int, season: schemas.SeasonUpdateSchemas):
    async with db() as session:
        result = await session.execute(
            stmt=select(Season).filter(Season.id == season_id)
        )
        db_season = result.scalars().first()

        if db_season is None:
            return None

        for key, value in season.model_dump().items():
            setattr(db_season, key, value)

        await session.commit()
        await session.refresh(db_season)
        return db_season


async def delete_season(db: AsyncSession, season_id: int):
    async with db() as session:
        stmt = select(Season).filter(Season.id == season_id)
        result = await session.execute(stmt)
        db_season = result.scalars().first()

        if db_season is None:
            return None

        await session.delete(db_season)
        await session.commit()
        return db_season


async def link_season_team(db: AsyncSession, season_id: int, team_id: int):
    # Перевіряємо, чи існує сезон
    season = await db.execute(select(Season).filter_by(id=season_id))
    season = season.scalars().first()
    if not season:
        raise HTTPException(status_code=404, detail="Season not found")

    # Перевіряємо, чи існує команда
    team = await db.execute(select(Team).filter_by(id=team_id))
    team = team.scalars().first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    # Створюємо зв'язок між сезоном і командою (Team_Season table)
    new_link = TeamSeason(season_id=season_id, team_id=team_id)
    db.add(new_link)

    try:
        await db.commit()  # Фіксуємо зміни в базі даних
    except Exception as e:
        await db.rollback()  # Відкат транзакції у разі помилки
        raise HTTPException(status_code=500, detail="Database commit failed")


async def delete_season_team(db: AsyncSession, season_id: int, team_id: int):
    """Видалення запису в таблиці-медіаторі (m2m) Сезон-Команда"""

    try:
        # Отримання сезону з командами через select з завантаженням асоціацій
        stmt_season = (
            select(Season)
            .options(selectinload(Season.teams_associations))
            .filter(Season.id == season_id)
        )
        season_result = await db.execute(stmt_season)
        season = season_result.scalars().first()

        # Отримання команди
        stmt_team = select(Team).filter(Team.id == team_id)
        team_result = await db.execute(stmt_team)
        team = team_result.scalars().first()

        # Перевірка, чи знайдено обидва об'єкти
        if not season:
            raise NoResultFound(f"Сезон з ID {season_id} не знайдено")
        if not team:
            raise NoResultFound(f"Команду з ID {team_id} не знайдено")

        # Перевірка, чи є команда в списку асоціацій сезону
        if team in season.teams_associations:
            season.teams_associations.remove(team)
            await db.commit()
            return season
        else:
            raise ValueError(f"Команда з ID {team_id} не є частиною сезону {season_id}")

    except NoResultFound as e:
        print(f"Помилка: {e}")
        return None
    except Exception as e:
        print(f"Інша помилка: {e}")
        return None
