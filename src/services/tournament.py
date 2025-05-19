from sqlalchemy import desc, select, asc, func
from sqlalchemy.ext.asyncio import AsyncSession
from models import Tournament, Region, Organization, Season, Team
from validation import tournament as schemas


async def get_tournament(db: AsyncSession, tournament_id: int):
    result = await db.execute(select(Tournament).filter(Tournament.id == tournament_id))
    return result.mappings().first()


async def get_tournament_slug(db: AsyncSession, tournament_slug: str):
    """Отримує деталі турніру за slug"""

    stmt = (
        select(
            Tournament.id,
            Tournament.slug,
            Tournament.logo,
            Tournament.name,
            Tournament.full_name,
            Tournament.create_year,
            Tournament.level_int,
            Tournament.level_up,
            Tournament.level_down,
            Tournament.website,
            Organization.tournament_level,
            Season.id,
            Season.slug,
            Region.name.label("region_name"),
        )
        .join(Season, Season.tournament_id == Tournament.id)
        .join(Organization, Organization.id == Tournament.organization_id)
        .join(Region, Region.id == Organization.region_id)
        .filter(Tournament.slug == tournament_slug)
    )

    result = await db.execute(stmt)
    return result.mappings().first()


async def get_tournament_for_season(db: AsyncSession, season_id: int = None, season_slug: str = None, **kwargs):
    """Отримує турнір для сезону за ідентифікатором або slug (асинхронно)"""

    stmt = (
        select(
            Tournament.logo,
            Tournament.name,
            Tournament.full_name,
            Tournament.create_year,
            Tournament.level_int,
            Tournament.level_up,
            Tournament.level_down,
            Tournament.website,
            Tournament.description,
            Organization.tournament_level,
            Season.id,
            Season.slug,
        )
        .join(Season, Season.tournament_id == Tournament.id)
        .join(Organization, Organization.id == Tournament.organization_id)
    )

    if season_id is not None:
        stmt = stmt.filter(Season.id == season_id)
    elif season_slug is not None:
        stmt = stmt.filter(Season.slug == season_slug)
    else:
        return None  # або викликати виключення, якщо обидва параметри None

    result = await db.execute(stmt)
    return result.mappings().first()


async def get_tournament_archive(db: AsyncSession, tournament_slug: str):
    """Отримує архів сезонів для турніру за slug"""

    stmt = (
        select(
            Season.slug.label("season_slug"),
            Season.name.label("season_name"),
            Season.full_name.label("season_full_name"),
            Season.year.label("season_year"),
            Region.slug.label("region_slug"),
            Team.slug.label("team_winner_slug"),
            Team.name.label("team_winner_name"),
            Team.city.label("team_winner_city"),
            Team.logo.label("team_winner_logo"),
        )
        .join(Tournament, Tournament.id == Season.tournament_id)
        .join(Organization, Organization.id == Tournament.organization_id)
        .join(Region, Region.id == Organization.region_id)
        .join(Team, Team.id == Season.team_winner_id, isouter=True)
        .filter(Tournament.slug == tournament_slug)
        .order_by(Season.year.desc())
    )

    result = await db.execute(stmt)
    return result.mappings().all()


async def get_tournaments(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(Tournament).offset(skip).limit(limit))
    return result.scalars().all()


async def get_region_tournaments(db: AsyncSession, region_id: int = None, region_slug: str = None, ** kwargs):
    """Вибірка всіх турнірів відповідного регіону"""

    stmt = (
        select(
            Season.slug.label("season_slug"),
            Tournament.slug.label('tournament_slug'),
            Tournament.name.label("tournament_name"),
            Tournament.full_name.label("tournament_full_name"),
            Tournament.logo.label("tournament_logo"),
            Tournament.football_type.label("football_type"),
            Organization.id.label("organization_id"),
            Organization.name.label("organization_name"),
            Organization.full_name.label("organization_full_name"),
            Organization.tournament_level.label("organization_level"),
            Organization.slug.label("organization_slug"),
            Region.slug.label("region_slug"),
        )
        .join(Tournament, Tournament.id == Season.tournament_id)
        .join(Organization, Organization.id == Tournament.organization_id)
        .join(Region, Region.id == Organization.region_id)
        .group_by(Tournament.full_name)  # Групування по турніру
        .order_by(asc(Tournament.id), desc(func.max(Season.end_date)))  # Сортування за ID турніру
    )

    if region_id is not None:
        stmt = stmt.filter(Region.id == region_id)
    elif region_slug is not None:
        stmt = stmt.filter(Region.slug == region_slug)
    else:
        return None  # або викликати виключення, якщо обидва параметри None

    result = await db.execute(stmt)
    return result.all()


async def create_tournament(db: AsyncSession, tournament: schemas.TournamentCreateSchemas):
    db_tournament = Tournament(**tournament.dict())
    async with db.begin():
        db.add(db_tournament)
        await db.flush()
    await db.refresh(db_tournament)
    return db_tournament


async def update_tournament(db: AsyncSession, tournament_id: int, tournament: schemas.TournamentUpdateSchemas):
    async with db.begin():  # Асинхронний контекст для транзакції
        result = await db.execute(
            select(Tournament).filter(Tournament.id == tournament_id)
        )
        db_tournament = result.scalars().first()

        if db_tournament is None:
            return None

        for key, value in tournament.dict().items():
            setattr(db_tournament, key, value)

        await db.flush()
        await db.refresh(db_tournament)


async def delete_tournament(db: AsyncSession, tournament_id: int):
    async with db.begin():  # Асинхронний контекст для транзакції
        result = await db.execute(
            select(Tournament).filter(Tournament.id == tournament_id)
        )
        db_tournament = result.scalars().first()

        if db_tournament is None:
            return None

        await db.delete(db_tournament)
        await db.commit()

    return db_tournament


# def create_tournament(db: Session, tournament: schemas.TournamentCreateSchemas):
#     db_tournament = Tournament(**tournament.dict())
#     db.add(db_tournament)
#     db.commit()
#     db.refresh(db_tournament)
#     return db_tournament


# def update_tournament(
#     db: Session, tournament_id: int, tournament: schemas.TournamentUpdateSchemas
# ):
#     db_tournament = db.query(Tournament).filter(Tournament.id == tournament_id).first()
#     if db_tournament is None:
#         return None
#     for key, value in tournament.dict().items():
#         setattr(db_tournament, key, value)
#     db.commit()
#     db.refresh(db_tournament)
#     return db_tournament


# def delete_tournament(db: Session, tournament_id: int):
#     db_tournament = db.query(Tournament).filter(Tournament.id == tournament_id).first()
#     if db_tournament is None:
#         return None
#     db.delete(db_tournament)
#     db.commit()
#     return db_tournament
