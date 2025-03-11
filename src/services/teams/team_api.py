from sqlalchemy import func, case, desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from models import (
    Team,
    Region,
    TeamSeason,
    Season,
)


async def get_all_teams(db: AsyncSession, team_name: str = None, team_city: str = None, region_name: str = None):
    """Функція отримання списку команд з можливістю фільтрації"""

    stmt = (
        select(
            Team.id,
            Team.slug,
            Team.logo,
            Team.name,
            Team.city,
            Team.full_name,
            Region.name.label("region_name"),
        )
        .join(Region, Region.id == Team.region_id)  # З'єднання з таблицею Region
        .order_by(Team.name)  # Сортування по назві команди
    )

    # Додаємо фільтрацію, якщо передані параметри
    if team_name:
        stmt = stmt.where(Team.name.ilike(f"%{team_name}%"))
    if team_city:
        stmt = stmt.where(Team.city.ilike(f"%{team_city}%"))
    if region_name:
        stmt = stmt.where(Region.name.ilike(f"%{region_name}%"))

    result = await db.execute(stmt)
    team_list = result.mappings().all()  # Отримання результату у вигляді словників

    return team_list


async def get_teams_in_season(db: AsyncSession, season_slug: str):
    """function to get a list of teams from a season"""

    stmt = (
        select(
            Team.id,
            Team.slug,
            Team.logo,
            Team.name,
            Team.city,
            Team.full_name,
            Region.name.label("region_name"),
            Season.id.label("season_id"),
            Season.slug.label("season_slug"),
        )
        .join(Region, Region.id == Team.region_id)  # З'єднання з Region
        .join(TeamSeason, TeamSeason.team_id == Team.id)  # З'єднання з TeamSeason
        .join(Season, Season.id == TeamSeason.season_id)  # З'єднання з Season
        .filter(Season.slug == season_slug)  # Фільтр по slug сезону
        .order_by(Team.name)  # Сортування по імені команди
    )

    result = await db.execute(stmt)
    team_list = result.all()  # Отримання всіх результатів як список кортежів

    # Формування результату у вигляді JSON
    teams = [
        {
            "id": team[0],  # team.id
            "slug": team[1],  # team.slug
            "logo": team[2],  # team.logo
            "name": team[3],  # team.name
            "city": team[4],  # team.city
            "full_name": team[5],  # team.full_name
            "region_name": team[6],  # region.name (поле region)
            "season_id": team[7],  # season.id
            "season_slug": team[8],  # season.slug
        }
        for team in team_list  # Кожен team — це кортеж з вибраними полями
    ]

    return teams
