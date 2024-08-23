from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List

from core.templating import templates
from core.database import get_db
from models import Group
from services import region as crud
from services.match import (
    get_matches_season,
    get_matches_results_season,
    get_matches_upcoming_season,
    get_matches_round,
)
from services.news_list import get_news_list_region
from services.region import get_regions
from services.season import (
    get_seasons_region,
    get_season_by_id_or_slug,
    get_season_tournament,
)
from services.stage import get_distinct_stages_with_groups
from services.standings import get_calculate_standings
from services.team import get_regions_team_list
from services.tournament import get_region_tournaments
from validation import region as schemas_region, match as schemas_match
from validation.season import SeasonSchemas

router = APIRouter()


@router.get("/", response_model=List[schemas_region.RegionSchemas])
def read_regions(request: Request, db: Session = Depends(get_db)):
    """виводить список регіонів"""

    regions = get_regions(db)

    return templates.TemplateResponse(
        "regions.html",
        {
            "request": request,
            "regions": regions,
        },
    )


@router.get("/{region_slug}", response_model=schemas_region.RegionSchemas)
def read_region(request: Request, region_slug: str, db: Session = Depends(get_db)):
    """виводить окремий регіон"""

    regions_list = get_regions(db)
    seasons_region = get_seasons_region(db, region_slug=region_slug)

    news_list_region = get_news_list_region(db, region_slug=region_slug)
    region = get_regions(db, region_slug=region_slug)
    tournaments = get_region_tournaments(db, region_slug=region_slug)

    if region is None:
        raise HTTPException(status_code=404, detail="Region not found")
    return templates.TemplateResponse(
        "region.html",
        {
            "request": request,
            "regions_list": regions_list,  # Список регіонів (бокове меню)
            "seasons": seasons_region,  # Список цьогорічних турнірів
            "news_list": news_list_region,  # Стрічка новин (даного регіону)
            "region": region,  # Виводить всю необхідну інформацію по даному регіону
            "tournaments": tournaments,
        },
    )


@router.get("/{region_slug}/teams", response_model=schemas_region.RegionSchemas)
def read_region(request: Request, region_slug: str, db: Session = Depends(get_db)):
    """виводить окремий регіон"""

    regions_list = get_regions(db)
    seasons_region = get_seasons_region(db, region_slug=region_slug)
    teams_list = get_regions_team_list(db, region_slug=region_slug)
    region = get_regions(db, region_slug=region_slug)

    if region is None:
        raise HTTPException(status_code=404, detail="Region not found")
    return templates.TemplateResponse(
        "region_teams.html",
        {
            "request": request,
            "regions_list": regions_list,  # Список регіонів (бокове меню)
            "seasons": seasons_region,  # Список цьогорічних турнірів
            "teams": teams_list,
            "region": region,  # Виводить всю необхідну інформацію по даному регіону
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
    season_slug: str,
    db: Session = Depends(get_db),
):

    regions_list = get_regions(db)
    seasons_region = get_seasons_region(db, region_slug=region_slug)
    matches = get_matches_season(db, season_id=season_id)
    rounds = get_matches_round(db, season_id=season_id)
    standings = get_calculate_standings(db=db, season_id=season_id)
    region = get_regions(db, region_slug=region_slug)
    season = get_season_by_id_or_slug(db, season_id=season_id)

    return templates.TemplateResponse(
        "matches/region_matches.html",
        {
            "request": request,
            "regions_list": regions_list,  # Список регіонів (бокове меню)
            "seasons": seasons_region,  # Список цьогорічних турнірів
            "matches": matches,
            "rounds": rounds,
            "standings": standings,
            "region": region,  # Виводить всю необхідну інформацію по даному регіону
            "season": season,
        },
    )


@router.get(
    "/{region_slug}/{season_slug}/{season_id}/results",
    response_model=List[schemas_match.MatchSchemas],
)
def region_season_matches_results(
    request: Request,
    region_slug: str,
    season_id: int,
    db: Session = Depends(get_db),
):

    regions_list = get_regions(db)
    seasons_region = get_seasons_region(db, region_slug=region_slug)

    standings = get_calculate_standings(db=db, season_id=season_id)
    region = get_regions(db, region_slug=region_slug)
    season = get_season_by_id_or_slug(db, season_id=season_id)
    matches_results = get_matches_results_season(db, season_id=season_id)

    return templates.TemplateResponse(
        "matches/region_matches.html",
        {
            "request": request,
            "regions_list": regions_list,  # Список регіонів (бокове меню)
            "seasons": seasons_region,  # Список цьогорічних турнірів
            "standings": standings,
            "region": region,  # Виводить всю необхідну інформацію по даному регіону
            "season": season,
            "matches": matches_results,
        },
    )


@router.get(
    "/{region_slug}/{season_slug}/{season_id}/upcoming",
    response_model=List[schemas_match.MatchSchemas],
)
def region_season_matches_upcoming(
    request: Request,
    region_slug: str,
    season_id: int,
    db: Session = Depends(get_db),
):

    regions_list = get_regions(db)
    seasons_region = get_seasons_region(db, region_slug=region_slug)
    standings = get_calculate_standings(db=db, season_id=season_id)
    region = get_regions(db, region_slug=region_slug)
    season = get_season_by_id_or_slug(db, season_id=season_id)
    matches_upcoming = get_matches_upcoming_season(db, season_id=season_id)

    return templates.TemplateResponse(
        "matches/region_matches.html",
        {
            "request": request,
            "regions_list": regions_list,  # Список регіонів (бокове меню)
            "seasons": seasons_region,  # Список цьогорічних турнірів
            "standings": standings,
            "region": region,  # Виводить всю необхідну інформацію по даному регіону
            "season": season,
            "matches": matches_upcoming,
        },
    )


# @router.get(
#     "/{region_slug}/{season_slug}/{season_id}/standings",
#     response_model=List[schemas_match.MatchSchemas],
# )
# def region_season_standings(
#     request: Request,
#     region_slug: str,
#     season_id: int,
#     group_id: int = None,  # Новий параметр для фільтрації по групах
#     db: Session = Depends(get_db),
# ):
#     regions_list = get_regions(db)
#     seasons_region = get_seasons_region(db, region_slug=region_slug)
#     standings = get_calculate_standings(db, season_id=season_id, group_id=group_id)
#     region = get_regions(db, region_slug=region_slug)
#     season = get_season_by_id_or_slug(db, season_id=season_id)
#     groups = (
#         db.query(Group).filter(Group.season_id == season_id).all()
#     )  # Отримання всіх груп сезону
#     stages = get_stages(db)
#
#     return templates.TemplateResponse(
#         "standings.html",
#         {
#             "request": request,
#             "regions_list": regions_list,
#             "seasons": seasons_region,
#             "standings": standings,
#             "region": region,
#             "season": season,
#             "groups": groups,  # Список груп
#             "stages": stages,  # Список стадій
#         },
#     )


@router.get(
    "/{region_slug}/{season_slug}/{season_id}/standings",
    response_model=List[schemas_match.MatchSchemas],
)
def region_season_standings(
    request: Request,
    region_slug: str,
    season_id: int,
    group_id: int = None,  # Новий параметр для фільтрації по групах
    db: Session = Depends(get_db),
):
    regions_list = get_regions(db)
    seasons_region = get_seasons_region(db, region_slug=region_slug)
    standings = get_calculate_standings(db, season_id=season_id)
    region = get_regions(db, region_slug=region_slug)
    season = get_season_by_id_or_slug(db, season_id=season_id)
    groups = (
        db.query(Group).filter(Group.season_id == season_id).all()
    )  # Отримання всіх груп сезону
    stages = get_distinct_stages_with_groups(db, season_id=season_id)

    return templates.TemplateResponse(
        "standings.html",
        {
            "request": request,
            "regions_list": regions_list,
            "seasons": seasons_region,
            "standings": standings,
            "region": region,
            "season": season,
            "groups": groups,  # Список груп
            "stages": stages,  # Список стадій
        },
    )


@router.get(
    "/{region_slug}/{season_slug}/{tournament_id}/archive",
    response_model=List[SeasonSchemas],
)
def region_seasons_tournament_archive(
    request: Request,
    region_slug: str,
    season_slug: str,
    tournament_id: int,
    db: Session = Depends(get_db),
):

    regions_list = get_regions(db)
    seasons_region = get_seasons_region(db, region_slug=region_slug)

    region = get_regions(db, region_slug=region_slug)
    season = get_season_by_id_or_slug(db, season_slug=season_slug)
    seasons_archive = get_season_tournament(db, tournament_id=tournament_id)

    return templates.TemplateResponse(
        "season_archive.html",
        {
            "request": request,
            "regions_list": regions_list,  # Список регіонів (бокове меню)
            "seasons": seasons_region,  # Список цьогорічних турнірів
            "region": region,  # Виводить всю необхідну інформацію по даному регіону
            "season": season,
            "seasons_archive": seasons_archive,
        },
    )


# для додавання нової області
@router.post("/", response_model=schemas_region.RegionSchemas)
def create_region(
    region: schemas_region.RegionCreateSchemas, db: Session = Depends(get_db)
):
    return crud.create_region(db=db, region=region)


# виводить список регіонів у swager
@router.get("/test", response_model=List[schemas_region.RegionSchemas])
def read_regions_test(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    regions = crud.get_regions(db, skip=skip, limit=limit)
    return regions


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
