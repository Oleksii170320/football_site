from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List

from core.templating import templates
from core.database import get_db
from models import Group
from services import region as crud
from services.contact import get_contact
from services.match import (
    get_season_matches_results,
    get_season_matches_upcoming,
    get_season_matches_weeks,
)
from services.news_list import get_news_list_region
from services.organization import get_organization, get_region_organization
from services.person import get_region_persons
from services.region import get_regions
from services.season import (
    get_seasons_region,
    get_season_by_id_or_slug,
    get_season_tournament,
)
from services.stage import get_distinct_stages_with_groups
from services.standings import get_calculate_standings
from services.team import get_regions_team_list
from services.tournament import (
    get_region_tournaments,
    get_tournament_slug,
    get_tournament_for_season,
)
from validation import region as schemas_region, match as schemas_match
from validation.season import SeasonSchemas

router = APIRouter()


@router.get("/", response_model=List[schemas_region.RegionSchemas])
def read_regions(request: Request, db: Session = Depends(get_db)):
    """Сторінка зі списком регіонів"""

    return templates.TemplateResponse(
        "regions.html",
        {
            "request": request,
            "regions": get_regions(db),
        },
    )


@router.get("/{region_slug}", response_model=schemas_region.RegionSchemas)
def read_region_by_slug(
        request: Request, region_slug: str, db: Session = Depends(get_db)
):
    """виводить окремий регіон по SLUG"""

    region = get_regions(db, region_slug=region_slug)

    if region is None:
        raise HTTPException(status_code=404, detail="Region not found")
    return templates.TemplateResponse(
        "region.html",
        {
            "request": request,
            "regions_list": get_regions(db),  # Список регіонів (бокове меню)
            "seasons": get_seasons_region(
                db, region_slug=region_slug
            ),  # Список цьогорічних турнірів
            "region": region,  # Виводить всю необхідну інформацію по даному регіону
            "news_list": get_news_list_region(
                db, region_slug=region_slug
            ),  # Стрічка новин (даного регіону)
        },
    )


@router.get("/{region_slug}/teams", response_model=schemas_region.RegionSchemas)
def region_teams(request: Request, region_slug: str, db: Session = Depends(get_db)):
    """Виводить команди даної області"""

    region = get_regions(db, region_slug=region_slug)

    if region is None:
        raise HTTPException(status_code=404, detail="Region not found")
    return templates.TemplateResponse(
        "region.html",
        {
            "request": request,
            "regions_list": get_regions(db),  # Список регіонів (бокове меню)
            "seasons": get_seasons_region(
                db, region_slug=region_slug
            ),  # Список цьогорічних турнірів
            "teams": get_regions_team_list(db, region_slug=region_slug),
            "region": region,  # Виводить всю необхідну інформацію по даному регіону/
            "region_teams": True,
        },
    )


@router.get("/{region_slug}/persons", response_model=schemas_region.RegionSchemas)
def region_persons(request: Request, region_slug: str, db: Session = Depends(get_db)):
    """Виводить всі дійові персони даної області"""

    region = get_regions(db, region_slug=region_slug)

    if region is None:
        raise HTTPException(status_code=404, detail="Region not found")
    return templates.TemplateResponse(
        "region.html",
        {
            "request": request,
            "regions_list": get_regions(db),  # Список регіонів (бокове меню)
            "seasons": get_seasons_region(
                db, region_slug=region_slug
            ),  # Список цьогорічних турнірів
            "persons": get_region_persons(db, region_slug=region_slug),
            "region": region,  # Виводить всю необхідну інформацію по даному регіону/
            "region_persons": True,
        },
    )


@router.get("/{region_slug}/contacts", response_model=schemas_region.RegionSchemas)
def region_contacts(request: Request, region_slug: str, db: Session = Depends(get_db)):
    """Виводить контактні дані обласної організації"""

    region = get_regions(db, region_slug=region_slug)

    if region is None:
        raise HTTPException(status_code=404, detail="Region not found")
    return templates.TemplateResponse(
        "region.html",
        {
            "request": request,
            "regions_list": get_regions(db),  # Список регіонів (бокове меню)
            "seasons": get_seasons_region(
                db, region_slug=region_slug
            ),  # Список цьогорічних турнірів
            "region": region,  # Виводить всю необхідну інформацію по даному регіону/
            "contact": get_contact(db, region_slug=region_slug),
            "region_contacts": True,
        },
    )


@router.get("/{region_slug}/tournaments", response_model=schemas_region.RegionSchemas)
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
            "regions_list": get_regions(db),  # Список регіонів (бокове меню)
            "seasons": get_seasons_region(
                db, region_slug=region_slug
            ),  # Список цьогорічних турнірів
            "region": region,  # Виводить всю необхідну інформацію по даному регіону/
            "tournaments": get_region_tournaments(db, region_slug=region_slug),
            "organizations": get_region_organization(db, region_slug=region_slug),
            "region_tournaments": True,
        },
    )


@router.get(
    "/{region_slug}/{season_id}/{season_slug}",
    response_model=List[schemas_match.MatchSchemas],
)
def region_season(
    request: Request,
    region_slug: str,
    season_id: int,
        db: Session = Depends(get_db),
):
    """Відкриває головну сторінку певного роїіграшу/сезону"""

    return templates.TemplateResponse(
        "seasons/season.html",
        {
            "request": request,
            "regions_list": get_regions(db),  # Список регіонів (бокове меню)
            "seasons": get_seasons_region(
                db, region_slug=region_slug
            ),  # Список цьогорічних турнірів
            "region": get_regions(
                db, region_slug=region_slug
            ),  # Виводить всю необхідну інформацію по даному регіону
            "season": get_season_by_id_or_slug(db, season_id=season_id),
            "tournaments": get_tournament_for_season(db, season_id=season_id),
            "matches": get_season_matches_weeks(db, season_id=season_id),
            "main": True,
        },
    )


@router.get(
    "/{region_slug}/{season_slug}/{season_id}/main",
    response_model=List[schemas_match.MatchSchemas],
)
def region_season_main(
        request: Request,
        region_slug: str,
        season_id: int,
    db: Session = Depends(get_db),
):
    """Відкриває головну сторінку певного роїіграшу/сезону по кнопці ГОЛОВНА"""

    return templates.TemplateResponse(
        "seasons/season.html",
        {
            "request": request,
            "regions_list": get_regions(db),  # Список регіонів (бокове меню)
            "seasons": get_seasons_region(
                db, region_slug=region_slug
            ),  # Список цьогорічних турнірів
            "region": get_regions(
                db, region_slug=region_slug
            ),  # Виводить всю необхідну інформацію по даному регіону
            "matches": get_season_matches_weeks(db, season_id=season_id),
            "season": get_season_by_id_or_slug(db, season_id=season_id),
            "tournaments": get_tournament_for_season(db, season_id=season_id),
            "main": True,
        },
    )


@router.get(
    "/{region_slug}/{season_slug}/{season_id}/results",
    response_model=List[schemas_match.MatchSchemas],
)
def season_matches_results(
    request: Request,
    region_slug: str,
    season_id: int,
    db: Session = Depends(get_db),
):
    """Відкриває сторінку з зіграними матчами розіграшу"""

    return templates.TemplateResponse(
        "seasons/season.html",
        {
            "request": request,
            "regions_list": get_regions(db),  # Список регіонів (бокове меню)
            "seasons": get_seasons_region(
                db, region_slug=region_slug
            ),  # Список цьогорічних турнірів
            "region": get_regions(
                db, region_slug=region_slug
            ),  # Виводить всю необхідну інформацію по даному регіону
            "season": get_season_by_id_or_slug(db, season_id=season_id),
            "matches": get_season_matches_results(db, season_id=season_id),
            "results": True,
        },
    )


@router.get(
    "/{region_slug}/{season_slug}/{season_id}/upcoming",
    response_model=List[schemas_match.MatchSchemas],
)
def season_matches_upcoming(
    request: Request,
    region_slug: str,
    season_id: int,
    db: Session = Depends(get_db),
):
    """Відкриває сторінку зі ще не зіграними матчами розіграшу"""

    return templates.TemplateResponse(
        "seasons/season.html",
        {
            "request": request,
            "regions_list": get_regions(db),  # Список регіонів (бокове меню)
            "seasons": get_seasons_region(
                db, region_slug=region_slug
            ),  # Список цьогорічних турнірів
            "region": get_regions(
                db, region_slug=region_slug
            ),  # Виводить всю необхідну інформацію по даному регіону
            "season": get_season_by_id_or_slug(db, season_id=season_id),
            "matches": get_season_matches_upcoming(db, season_id=season_id),
            "upcoming": True,
        },
    )


@router.get(
    "/{region_slug}/{season_slug}/{season_id}/standings",
    response_model=List[schemas_match.MatchSchemas],
)
def season_standings(
    request: Request,
    region_slug: str,
    season_id: int,
    group_id: int = None,  # Новий параметр для фільтрації по групах
    db: Session = Depends(get_db),
):
    """Відкриває турніру таблицю розіграшу"""

    groups = db.query(Group).filter(Group.season_id == season_id).all()

    return templates.TemplateResponse(
        "seasons/season.html",
        {
            "request": request,
            "regions_list": get_regions(db),
            "seasons": get_seasons_region(db, region_slug=region_slug),
            "standings": get_calculate_standings(db, season_id=season_id),
            "region": get_regions(db, region_slug=region_slug),
            "season": get_season_by_id_or_slug(db, season_id=season_id),
            "groups": groups,  # Отримання всіх груп сезону,  # Список груп
            "stages": get_distinct_stages_with_groups(
                db, season_id=season_id
            ),  # Список стадій
        },
    )


@router.get(
    "/{region_slug}/{season_slug}/{tournament_id}/archive",
    response_model=List[SeasonSchemas],
)
def tournament_archive(
    request: Request,
    region_slug: str,
    season_slug: str,
    tournament_id: int,
    db: Session = Depends(get_db),
):
    """Відкриває історію розіграшів турніру"""

    return templates.TemplateResponse(
        "seasons/season.html",
        {
            "request": request,
            "regions_list": get_regions(db),  # Список регіонів (бокове меню)
            "seasons": get_seasons_region(
                db, region_slug=region_slug
            ),  # Список цьогорічних турнірів
            "region": get_regions(
                db, region_slug=region_slug
            ),  # Виводить всю необхідну інформацію по даному регіону
            "season": get_season_by_id_or_slug(db, season_slug=season_slug),
            "seasons_archive": get_season_tournament(db, tournament_id=tournament_id),
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
