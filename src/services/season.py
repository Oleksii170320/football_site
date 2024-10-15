import logging
from datetime import datetime

from fastapi import HTTPException
from sqlalchemy import desc, func, select, insert
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session, selectinload
from starlette.responses import JSONResponse

from models import (
    Season,
    Team,
    Tournament,
    Organization,
    Association,
    Region,
    TeamSeason,
)
from services.team import get_team_for_id
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
            Season.year.label("season_year"),
            Region.slug.label("region_slug"),
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
            Season.year.label("season_year"),
            Region.slug.label("region_slug"),
            Association.name.label("association_name"),
            Organization.name.label("organization_name"),
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


async def get_season_by_id_or_slug(
    db: AsyncSession, season_id: int = None, season_slug: str = None, **kwargs
):
    """Отримує сезон за ідентифікатором або slug (асинхронно)"""
    stmt = select(
        Season.id.label("season_id"),
        Season.slug.label("season_slug"),
        Season.name.label("season_name"),
        Season.year.label("season_year"),
        Season.standing,
        Tournament.logo.label("tournament_logo"),
        Tournament.slug.label("tournament_slug"),
    ).join(Tournament, Tournament.id == Season.tournament_id)
    if season_id is not None:
        stmt = stmt.filter(Season.id == season_id)
    elif season_slug is not None:
        stmt = stmt.filter(Season.slug == season_slug)
    else:
        return None  # або викликати виключення, якщо обидва параметри None

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

    # Логіка для прив'язки команди до сезону
    # Наприклад, якщо у вас є таблиця для зв'язків, ви можете створити запис тут
    # Пряме прив'язування до сезону
    season.teams.append(team)  # Додайте команду до списку команд сезону

    # Збережіть зміни в базі даних
    await db.commit()

    # Перетворення команди на словник для Pydantic
    team_data = team.to_dict()  # Використання методу to_dict()

    # Використання Pydantic для створення TeamSchemas
    team_schema = TeamSchemas.from_orm(team_data)

    return team_schema


async def get_seasons_region(
    db: AsyncSession, region_slug: str, season_slug: str = None, **kwargs
):
    current_year = datetime.now().year

    stmt = (
        select(
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
        .order_by(desc(Season.end_date))
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


async def update_season(
    db: AsyncSession, season_id: int, season: schemas.SeasonUpdateSchemas
):
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


# def link_season_team(db: Session, season_id: int, team_id: int):
#     """Створення запису в таблиці-медіаторі (m2m) Сезон-кКоманда"""
#
#     season = db.query(Season).filter(Season.id == season_id).first()
#     team = db.query(Team).filter(Team.id == team_id).first()
#     season.teams_associations.append(team)
#     db.commit()
#     return season


# async def link_season_team(db: AsyncSession, season_id: int, team_id: int):
#     # Створюємо транзакцію
#     async with db.begin():
#         season_result = await db.execute(select(Season).filter(Season.id == season_id))
#         # team_result = await db.execute(select(Team).filter(Team.id == team_id))
#
#         season = season_result.scalars().first()
#         team = await get_team_for_id(db, team_id=team_id)
#
#         if not season:
#             raise HTTPException(status_code=404, detail="Сезон не знайдений")
#         if not team:
#             raise HTTPException(status_code=404, detail="Команда не знайдена")
#
#         # Додаємо команду до сезону
#         await db.execute(
#             insert(TeamSeason).values(season_id=season.id, team_id=team.id)
#         )
#         await db.commit()
#
#         # Перетворюємо об'єкт команди у схему Pydantic
#         teams = [TeamSchemas.from_orm(team).dict()]
#
#         return JSONResponse(content={"status": "success", "teams": teams})


# async def link_season_team(db: AsyncSession, season_id: int, team_id: int):
#     async with db.begin():
#         season = await get_season_for_id(db, season_id=season_id)
#         team = await get_team_for_id(db, team_id=team_id)
#
#         if not season:
#             raise HTTPException(status_code=404, detail="Сезон не знайдений")
#         if not team:
#             raise HTTPException(status_code=404, detail="Команда не знайдена")
#
#         # Додаємо команду до сезону
#         season.teams_associations.append(team)  # не потрібно використовувати await
#         await db.commit()
#
#         return JSONResponse(content={"status": "success", "teams": team.name})


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
