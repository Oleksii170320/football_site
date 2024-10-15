from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from core.templating import render
from core.database import get_db
from services import region as crud, get_context_data
from services.contact import get_contact
from services.group import get_group_in_season, get_groups
from services.match import (
    get_season_matches_results,
    get_season_matches_upcoming,
    get_season_all_matches,
)
from services.news_list import get_news_list_region
from services.organization import get_region_organization
from services.person import get_region_persons
from services.region import get_regions, get_regions_list, get_region
from services.round import get_rounds
from services.season import get_seasons_region, get_season_by_id_or_slug
from services.stadium import get_all_stadiums
from services.stage import get_distinct_stages_with_groups, get_stages
from services.standings import get_calculate_standings
from services.team import get_regions_team_list, get_teams_in_season, get_teams
from services.tournament import (
    get_region_tournaments,
    get_tournament_archive,
    get_tournament_for_season,
)
from validation import region as schemas_region

router = APIRouter()


@router.get("/")
async def read_regions(request: Request, db: AsyncSession = Depends(get_db)):
    """Сторінка зі списком регіонів"""

    return render(
        "regions.html",
        request,
        {
            "regions_list": await get_regions_list(db),
            "regions": await get_regions(db),
        },
    )


@router.get("/{region_slug}")
async def read_region_by_slug(
    request: Request, region_slug: str, db: AsyncSession = Depends(get_db)
):
    """виводить окремий регіон по SLUG"""

    return render(
        "region.html",
        request,
        {
            "regions_list": await get_regions_list(db),  # Список регіонів (бокове меню)
            "seasons": await get_seasons_region(db, region_slug=region_slug),
            "region": await get_region(db, region_slug=region_slug),
            "news_list": await get_news_list_region(db, region_slug=region_slug),
        },
    )


@router.get("/{region_slug}/tournaments")
async def region_tournaments(
    request: Request, region_slug: str, db: AsyncSession = Depends(get_db)
):
    """Виводить всі футбольні та футзальні турніри даної області"""

    return render(
        "region.html",
        request,
        {
            "regions_list": await get_regions_list(db),  # Список регіонів (бокове меню)
            "seasons": await get_seasons_region(db, region_slug=region_slug),
            "region": await get_regions(db, region_slug=region_slug),
            "tournaments": await get_region_tournaments(db, region_slug=region_slug),
            "organizations": await get_region_organization(db, region_slug=region_slug),
            "region_tournaments": True,
        },
    )


@router.get("/{region_slug}/teams")
async def region_teams(
    request: Request, region_slug: str, db: AsyncSession = Depends(get_db)
):
    """Виводить команди даної області"""

    return render(
        "region.html",
        request,
        {
            "regions_list": await get_regions_list(db),  # Список регіонів (бокове меню)
            "seasons": await get_seasons_region(db, region_slug=region_slug),
            "teams": await get_regions_team_list(db, region_slug=region_slug),
            "region": await get_regions(db, region_slug=region_slug),
            "region_teams": True,
        },
    )


@router.get("/{region_slug}/persons")
async def region_persons(
    request: Request, region_slug: str, db: AsyncSession = Depends(get_db)
):
    """Виводить всі дійові персони даної області"""

    return render(
        "region.html",
        request,
        {
            "regions_list": await get_regions_list(db),  # Список регіонів (бокове меню)
            "seasons": await get_seasons_region(db, region_slug=region_slug),
            "persons": await get_region_persons(db, region_slug=region_slug),
            "region": await get_regions(db, region_slug=region_slug),
            "region_persons": True,
        },
    )


@router.get("/{region_slug}/contacts")
async def region_contacts(
    request: Request, region_slug: str, db: AsyncSession = Depends(get_db)
):
    """Виводить контактні дані обласної організації"""

    return render(
        "region.html",
        request,
        {
            "regions_list": await get_regions_list(db),  # Список регіонів (бокове меню)
            "seasons": await get_seasons_region(db, region_slug=region_slug),
            "region": await get_regions(db, region_slug=region_slug),
            "contact": await get_contact(db, region_slug=region_slug),
            "region_contacts": True,
        },
    )


@router.get("/{region_slug}/{season_slug}")
async def region_season(
    request: Request,
    region_slug: str,
    season_slug: str,
    db: Session = Depends(get_db),
):
    """Відкриває головну сторінку певного розіграшу/сезону"""

    return render(
        "seasons/season.html",
        request,
        {
            "regions_list": await get_regions_list(db),  # Список регіонів (бокове меню)
            "seasons": await get_seasons_region(db, region_slug=region_slug),
            "region": await get_regions(db, region_slug=region_slug),
            "season": await get_season_by_id_or_slug(db, season_slug=season_slug),
            "matches": await get_season_matches_results(db, season_slug=season_slug),
            "tournaments": await get_tournament_for_season(db, season_slug=season_slug),
            "main": True,
        },
    )


@router.get("/{region_slug}/{season_slug}/main")
async def region_season_main(
    request: Request,
    region_slug: str,
    season_slug: str,
    db: AsyncSession = Depends(get_db),
):
    """Відкриває головну сторінку певного роїіграшу/сезону по кнопці ГОЛОВНА"""

    return render(
        "seasons/season.html",
        request,
        {
            "regions_list": await get_regions_list(db),  # Список регіонів (бокове меню)
            "seasons": await get_seasons_region(db, region_slug=region_slug),
            "region": await get_regions(db, region_slug=region_slug),
            "season": await get_season_by_id_or_slug(db, season_slug=season_slug),
            "matches": await get_season_matches_results(db, season_slug=season_slug),
            "tournaments": await get_tournament_for_season(db, season_slug=season_slug),
            "main": True,
        },
    )


@router.get("/{region_slug}/{season_slug}/results")
async def season_matches_results(
    request: Request,
    region_slug: str,
    season_slug: str,
    db: Session = Depends(get_db),
):
    """Відкриває сторінку з зіграними матчами розіграшу"""

    return render(
        "seasons/season.html",
        request,
        {
            "regions_list": await get_regions_list(db),
            "seasons": await get_seasons_region(db, region_slug=region_slug),
            "region": await get_regions(db, region_slug=region_slug),
            "season": await get_season_by_id_or_slug(db, season_slug=season_slug),
            "matches": await get_season_matches_results(db, season_slug=season_slug),
            "results": True,
        },
    )


@router.get("/{region_slug}/{season_slug}/upcoming")
async def season_matches_upcoming(
    request: Request,
    region_slug: str,
    season_slug: str,
    db: AsyncSession = Depends(get_db),
):
    """Відкриває сторінку зі ще не зіграними матчами розіграшу"""

    return render(
        "seasons/season.html",
        request,
        {
            "regions_list": await get_regions_list(db),
            "seasons": await get_seasons_region(db, region_slug=region_slug),
            "region": await get_regions(db, region_slug=region_slug),
            "season": await get_season_by_id_or_slug(db, season_slug=season_slug),
            "matches": await get_season_matches_upcoming(db, season_slug=season_slug),
            "upcoming": True,
        },
    )


@router.get("/{region_slug}/{season_slug}/standings")
async def season_standings(
    request: Request,
    region_slug: str,
    season_slug: str,
    db: AsyncSession = Depends(get_db),
):
    """Відкриває турніру таблицю розіграшу"""

    return render(
        "seasons/season.html",
        request,
        {
            "regions_list": await get_regions_list(db),
            "seasons": await get_seasons_region(db, region_slug=region_slug),
            "standings": await get_calculate_standings(db, season_slug=season_slug),
            "region": await get_regions(db, region_slug=region_slug),
            "season": await get_season_by_id_or_slug(db, season_slug=season_slug),
            "groups": await get_group_in_season(db, season_slug=season_slug),
            "stages": await get_distinct_stages_with_groups(
                db, season_slug=season_slug
            ),
        },
    )


@router.get("/{region_slug}/{season_id}/{tournament_slug}/archive")
async def tournament_archive(
    request: Request,
    region_slug: str,
    season_id: int,
    tournament_slug: str,
    db: AsyncSession = Depends(get_db),
):
    """Відкриває історію розіграшів турніру"""

    return render(
        "seasons/season.html",
        request,
        {
            "regions_list": await get_regions_list(db),
            "seasons": await get_seasons_region(db, region_slug=region_slug),
            "region": await get_regions(db, region_slug=region_slug),
            "season": await get_season_by_id_or_slug(db, season_id=season_id),
            "seasons_archive": await get_tournament_archive(
                db, tournament_slug=tournament_slug
            ),
        },
    )


@router.get("/{region_slug}/{season_slug}/clubs")
async def tournament_archive(
    request: Request,
    region_slug: str,
    season_slug: str,
    db: AsyncSession = Depends(get_db),
):
    """Відкриває історію розіграшів турніру"""

    return render(
        "seasons/season.html",
        request,
        {
            "regions_list": await get_regions_list(db),  # Список регіонів (бокове меню)
            "seasons": await get_seasons_region(db, region_slug=region_slug),
            "region": await get_regions(db, region_slug=region_slug),
            "season": await get_season_by_id_or_slug(db, season_slug=season_slug),
            "teams": await get_teams_in_season(db, season_slug=season_slug),
            "add_team": await get_teams(db),
            "seasons_clubs": True,
        },
    )


@router.get("/{region_slug}/{season_slug}/schedule")
async def tournament_archive(
    request: Request,
    region_slug: str,
    season_slug: str,
    db: AsyncSession = Depends(get_db),
):
    """Відкриває історію розіграшів турніру"""

    return render(
        "seasons/season.html",
        request,
        {
            "regions_list": await get_regions_list(db),  # Список регіонів (бокове меню)
            "seasons": await get_seasons_region(db, region_slug=region_slug),
            "region": await get_regions(db, region_slug=region_slug),
            "season": await get_season_by_id_or_slug(db, season_slug=season_slug),
            "matches": await get_season_all_matches(db, season_slug=season_slug),
            "teams": await get_teams_in_season(db, season_slug=season_slug),
            "stages": await get_stages(db),
            "groups": await get_groups(db),
            "rounds": await get_rounds(db),
            "stadiums": await get_all_stadiums(db),
            "seasons_schedule": True,
        },
    )


@router.get("/{region_slug}/{season_slug}/schedule/teas")
async def tournament_archive(
    request: Request,
    region_slug: str,
    season_slug: str,
    db: AsyncSession = Depends(get_db),
):
    """Відкриває історію розіграшів турніру"""

    return render(
        # "seasons/season.html",
        "index.html",
        request,
        {
            "regions_list": await get_regions_list(db),  # Список регіонів (бокове меню)
            "seasons": await get_seasons_region(db, region_slug=region_slug),
            "region": await get_regions(db, region_slug=region_slug),
            "season": await get_season_by_id_or_slug(db, season_slug=season_slug),
            "matches": await get_season_all_matches(db, season_slug=season_slug),
            "teams": await get_teams_in_season(db, season_slug=season_slug),
            "stages": await get_stages(db),
            "groups": await get_groups(db),
            "rounds": await get_rounds(db),
            "stadiums": await get_all_stadiums(db),
            "seasons_schedule": True,
        },
    )


# Спеціальні запити CRUD
@router.post("/", response_model=schemas_region.RegionSchemas)
async def create_region(
    region: schemas_region.RegionCreateSchemas, db: AsyncSession = Depends(get_db)
):
    """Додає новий регіон/область"""
    return await crud.create_region(db=db, region=region)


@router.put("/{region_id}", response_model=schemas_region.RegionSchemas)
async def update_region(
    region_id: int,
    region: schemas_region.RegionUpdateSchemas,
    db: AsyncSession = Depends(get_db),
):
    db_region = await crud.update_region(db=db, region_id=region_id, region=region)
    if db_region is None:
        raise HTTPException(status_code=404, detail="Region not found")
    return db_region


@router.delete("/{region_id}", response_model=schemas_region.RegionSchemas)
async def delete_region(region_id: int, db: AsyncSession = Depends(get_db)):
    db_region = await crud.delete_region(db=db, region_id=region_id)
    if db_region is None:
        raise HTTPException(status_code=404, detail="Region not found")
    return db_region
