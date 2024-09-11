from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List

from core.templating import templates
from core.database import get_db
from services import region as crud, get_context_data
from services.contact import get_contact
from services.group import get_group_in_season, get_groups
from services.match import (
    get_season_matches_results,
    get_season_matches_upcoming,
    get_season_matches_weeks,
)
from services.news_list import get_news_list_region
from services.organization import get_organization, get_region_organization
from services.person import get_region_persons
from services.region import get_regions, get_regions_list, get_region
from services.round import get_rounds_list
from services.season import (
    get_seasons_region,
    get_season_by_id_or_slug,
    get_season_tournament,
)
from services.stage import get_distinct_stages_with_groups, get_stages
from services.standings import get_calculate_standings
from services.team import get_regions_team_list, get_teams_in_season, get_teams
from services.tournament import (
    get_region_tournaments,
    get_tournament_for_season,
)
from validation import region as schemas_region, match as schemas_match
from validation.season import SeasonSchemas

router = APIRouter()


@router.get("/")
def read_regions(request: Request, db: Session = Depends(get_db)):
    """Сторінка зі списком регіонів"""

    return templates.TemplateResponse(
        "regions.html",
        {
            "request": request,
            "regions": get_regions(db),
        },
    )


@router.get("/{region_slug}")
def read_region_by_slug(
    request: Request, region_slug: str, db: Session = Depends(get_db)
):
    """виводить окремий регіон по SLUG"""

    return templates.TemplateResponse(
        "region.html",
        {
            "request": request,
            "regions_list": get_regions_list(db),  # Список регіонів (бокове меню)
            "seasons": get_seasons_region(
                db, region_slug=region_slug
            ),  # Список цьогорічних турнірів
            "region": get_region(
                db, region_slug=region_slug
            ),  # Виводить всю необхідну інформацію по даному регіону
            "news_list": get_news_list_region(
                db, region_slug=region_slug
            ),  # Стрічка новин (даного регіону)
        },
    )


@router.get("/{region_slug}/teams")
def region_teams(request: Request, region_slug: str, db: Session = Depends(get_db)):
    """Виводить команди даної області"""

    region = get_regions(db, region_slug=region_slug)

    if region is None:
        raise HTTPException(status_code=404, detail="Region not found")
    return templates.TemplateResponse(
        "region.html",
        {
            "request": request,
            "regions_list": get_regions_list(db),  # Список регіонів (бокове меню)
            "seasons": get_seasons_region(
                db, region_slug=region_slug
            ),  # Список цьогорічних турнірів
            "teams": get_regions_team_list(
                db, region_slug=region_slug
            ),  # List of teams of this region
            "region": region,  # Information of this region
            "region_teams": True,
        },
    )


@router.get("/{region_slug}/persons")
def region_persons(request: Request, region_slug: str, db: Session = Depends(get_db)):
    """Виводить всі дійові персони даної області"""

    region = get_regions(db, region_slug=region_slug)

    if region is None:
        raise HTTPException(status_code=404, detail="Region not found")
    return templates.TemplateResponse(
        "region.html",
        {
            "request": request,
            "regions_list": get_regions_list(db),  # Список регіонів (бокове меню)
            "seasons": get_seasons_region(
                db, region_slug=region_slug
            ),  # Список цьогорічних турнірів
            "persons": get_region_persons(db, region_slug=region_slug),
            "region": region,  # Виводить всю необхідну інформацію по даному регіону/
            "region_persons": True,
        },
    )


@router.get("/{region_slug}/contacts")
def region_contacts(request: Request, region_slug: str, db: Session = Depends(get_db)):
    """Виводить контактні дані обласної організації"""

    region = get_regions(db, region_slug=region_slug)

    if region is None:
        raise HTTPException(status_code=404, detail="Region not found")
    return templates.TemplateResponse(
        "region.html",
        {
            "request": request,
            "regions_list": get_regions_list(db),  # Список регіонів (бокове меню)
            "seasons": get_seasons_region(
                db, region_slug=region_slug
            ),  # Список цьогорічних турнірів
            "region": region,  # Виводить всю необхідну інформацію по даному регіону/
            "contact": get_contact(db, region_slug=region_slug),
            "region_contacts": True,
        },
    )


@router.get("/{region_slug}/tournaments")
def region_tournaments(
    request: Request, region_slug: str, db: Session = Depends(get_db)
):
    """Виводить всі футбольні та футзальні турніри даної області"""

    region = get_regions(db, region_slug=region_slug)

    if region is None:
        raise HTTPException(status_code=404, detail="Region not found")
    return templates.TemplateResponse(
        "region.html",
        {
            "request": request,
            "regions_list": get_regions_list(db),  # Список регіонів (бокове меню)
            "seasons": get_seasons_region(
                db, region_slug=region_slug
            ),  # Список цьогорічних турнірів
            "region": region,  # Виводить всю необхідну інформацію по даному регіону/
            "tournaments": get_region_tournaments(db, region_slug=region_slug),
            "organizations": get_region_organization(db, region_slug=region_slug),
            "region_tournaments": True,
        },
    )


@router.get("/{region_slug}/{season_slug}")
def region_season(request: Request, region_slug: str, season_slug: str):
    """Відкриває головну сторінку певного розіграшу/сезону"""

    context = get_context_data(
        request,
        [
            "regions_list",
            "seasons",
            "region",
            "season",
            "tournaments",
            "matches",
        ],
        season_slug=season_slug,
        region_slug=region_slug,
    )
    return templates.TemplateResponse(
        "seasons/season.html",
        {"request": request, "main": True, **context},
    )


@router.get("/{region_slug}/{season_slug}/main")
def region_season_main(request: Request, region_slug: str, season_slug: str):
    """Відкриває головну сторінку певного роїіграшу/сезону по кнопці ГОЛОВНА"""

    context = get_context_data(
        request,
        [
            "regions_list",
            "seasons",
            "region",
            "season",
            "tournaments",
            "matches",
        ],
        season_slug=season_slug,
        region_slug=region_slug,
    )
    return templates.TemplateResponse(
        "seasons/season.html",
        {"request": request, "main": True, **context},
    )


@router.get("/{region_slug}/{season_slug}/results")
def season_matches_results(
    request: Request,
    region_slug: str,
    season_slug: str,
    db: Session = Depends(get_db),
):
    """Відкриває сторінку з зіграними матчами розіграшу"""

    return templates.TemplateResponse(
        "seasons/season.html",
        {
            "request": request,
            "regions_list": get_regions_list(db),  # Список регіонів (бокове меню)
            "seasons": get_seasons_region(
                db, region_slug=region_slug
            ),  # Список цьогорічних турнірів
            "region": get_regions(
                db, region_slug=region_slug
            ),  # Виводить всю необхідну інформацію по даному регіону
            "season": get_season_by_id_or_slug(db, season_slug=season_slug),
            "matches": get_season_matches_results(db, season_slug=season_slug),
            "results": True,
        },
    )


@router.get("/{region_slug}/{season_slug}/upcoming")
def season_matches_upcoming(
    request: Request,
    region_slug: str,
    season_slug: str,
    db: Session = Depends(get_db),
):
    """Відкриває сторінку зі ще не зіграними матчами розіграшу"""

    return templates.TemplateResponse(
        "seasons/season.html",
        {
            "request": request,
            "regions_list": get_regions_list(db),  # Список регіонів (бокове меню)
            "seasons": get_seasons_region(
                db, region_slug=region_slug
            ),  # Список цьогорічних турнірів
            "region": get_regions(
                db, region_slug=region_slug
            ),  # Виводить всю необхідну інформацію по даному регіону
            "season": get_season_by_id_or_slug(db, season_slug=season_slug),
            "matches": get_season_matches_upcoming(db, season_slug=season_slug),
            "upcoming": True,
        },
    )


@router.get("/{region_slug}/{season_slug}/standings")
def season_standings(
    request: Request,
    region_slug: str,
    season_slug: str,
    db: Session = Depends(get_db),
):
    """Відкриває турніру таблицю розіграшу"""

    return templates.TemplateResponse(
        "seasons/season.html",
        {
            "request": request,
            "regions_list": get_regions_list(db),
            "seasons": get_seasons_region(db, region_slug=region_slug),
            "standings": get_calculate_standings(db, season_slug=season_slug),
            "region": get_regions(db, region_slug=region_slug),
            "season": get_season_by_id_or_slug(db, season_slug=season_slug),
            "groups": get_group_in_season(
                db, season_slug=season_slug
            ),  # Отримання всіх груп сезону,  # Список груп
            "stages": get_distinct_stages_with_groups(
                db, season_slug=season_slug
            ),  # Список стадій
        },
    )


@router.get("/{region_slug}/{season_id}/{tournament_slug}/archive")
def tournament_archive(
    request: Request,
    region_slug: str,
    season_id: int,
    tournament_slug: str,
    db: Session = Depends(get_db),
):
    """Відкриває історію розіграшів турніру"""

    return templates.TemplateResponse(
        "seasons/season.html",
        {
            "request": request,
            "regions_list": get_regions_list(db),  # Список регіонів (бокове меню)
            "seasons": get_seasons_region(
                db, region_slug=region_slug
            ),  # Список цьогорічних турнірів
            "region": get_regions(
                db, region_slug=region_slug
            ),  # Виводить всю необхідну інформацію по даному регіону
            "season": get_season_by_id_or_slug(db, season_id=season_id),
            "seasons_archive": get_season_tournament(
                db, tournament_slug=tournament_slug
            ),
        },
    )


@router.get("/{region_slug}/{season_slug}/clubs")
def tournament_archive(
    request: Request,
    region_slug: str,
    season_slug: str,
    db: Session = Depends(get_db),
):
    """Відкриває історію розіграшів турніру"""

    return templates.TemplateResponse(
        "seasons/season.html",
        {
            "request": request,
            "regions_list": get_regions_list(db),  # Список регіонів (бокове меню)
            "seasons": get_seasons_region(
                db, region_slug=region_slug
            ),  # Список цьогорічних турнірів
            "region": get_regions(
                db, region_slug=region_slug
            ),  # Виводить всю необхідну інформацію по даному регіону
            "season": get_season_by_id_or_slug(db, season_slug=season_slug),
            "teams": get_teams_in_season(db, season_slug=season_slug),
            "add_team": get_teams(db),
            "seasons_clubs": True,
        },
    )


@router.get("/{region_slug}/{season_slug}/schedule")
def tournament_archive(
    request: Request,
    region_slug: str,
    season_slug: str,
    db: Session = Depends(get_db),
):
    """Відкриває історію розіграшів турніру"""

    return templates.TemplateResponse(
        "seasons/season.html",
        {
            "request": request,
            "regions_list": get_regions_list(db),  # Список регіонів (бокове меню)
            "seasons": get_seasons_region(
                db, region_slug=region_slug
            ),  # Список цьогорічних турнірів
            "region": get_regions(
                db, region_slug=region_slug
            ),  # Виводить всю необхідну інформацію по даному регіону
            "season": get_season_by_id_or_slug(db, season_slug=season_slug),
            "teams": get_teams_in_season(db, season_slug=season_slug),
            "rounds": get_rounds_list(db),
            "groups": get_groups(db),
            "stages": get_stages(db),
            "seasons_schedule": True,
        },
    )


# для додавання нової області
@router.post("/", response_model=schemas_region.RegionSchemas)
def create_region(
    region: schemas_region.RegionCreateSchemas, db: Session = Depends(get_db)
):
    return crud.create_region(db=db, region=region)


# виводить список регіонів у swager
@router.get("/{region_id}/seasons")
def get_region_seasons(region_id: int, db: Session = Depends(get_db)):
    seasons = crud.get_region_seasons(db, region_id=region_id)
    region = crud.get_region(db, region_id=region_id)

    if not seasons:
        raise HTTPException(status_code=404, detail="Seasons not found")

    seasons_list = [{"name": season.name} for season in seasons]
    return {
        "seasons": seasons_list,
        "region_name": region.name,
        "region_emblem": region.emblem,
    }


@router.get("/{region_id}/tournaments", response_model=schemas_region.RegionSchemas)
def read_region_tournament(
    request: Request, region_id: int, db: Session = Depends(get_db)
):
    tournaments = crud.get_regions_for_tournament(db, region_id=region_id)


@router.put("/{region_id}", response_model=schemas_region.RegionSchemas)
def update_region(
    region_id: int,
    region: schemas_region.RegionUpdateSchemas,
    db: Session = Depends(get_db),
):
    db_region = crud.update_region(db=db, region_id=region_id, region=region)
    if db_region is None:
        raise HTTPException(status_code=404, detail="Region not found")
    return db_region


@router.delete("/{region_id}", response_model=schemas_region.RegionSchemas)
def delete_region(region_id: int, db: Session = Depends(get_db)):
    db_region = crud.delete_region(db=db, region_id=region_id)
    if db_region is None:
        raise HTTPException(status_code=404, detail="Region not found")
    return db_region
