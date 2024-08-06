from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from core.templating import templates

from core.database import get_db
from services import match as crud, region, standings as table
from services.match import get_matches_results_season, get_matches_upcoming_season
from services.news_list import get_news_list
from services.region import get_regions_list
from validation import match as schemas


router = APIRouter()


@router.get("/", response_model=List[schemas.MatchSchemas])
def read_matches(request: Request, db: Session = Depends(get_db)):

    news_list = get_news_list(db)
    regions_list = get_regions_list(db)
    matches = crud.get_matches(db)

    return templates.TemplateResponse(
        "matches.html",
        {
            "request": request,
            "news_list": news_list,  # Стрічка новин (всі регіони)
            "regions_list": regions_list,  # Список регіонів (бокове меню)
            "matches": matches,
        },
    )


@router.post("/", response_model=schemas.MatchSchemas)
def create_match(match: schemas.MatchCreateSchemas, db: Session = Depends(get_db)):
    return crud.create_match(db=db, match=match)


@router.get("/test", response_model=List[schemas.MatchSchemas])
def read_matches_test(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    matches = crud.get_matches(db, skip=skip, limit=limit)
    return matches


# @router.get("/tournament/{region_id}", response_model=List[schemas.MatchSchemas])
# def read_matches_season(
#     request: Request, region_id: int, db: Session = Depends(get_db)
# ):
#
#     regions_list = get_regions_list(db)
#     seasons_region = get_seasons_region_id(db, region_id=region_id)
#     # matches = crud.get_matches_season(db, region_id=region_id)
#     # standings = table.get_calculate_standings(db=db, region_id=region_id)
#
#     return templates.TemplateResponse(
#         "region_matches.html",
#         {
#             "request": request,
#             "regions_list": regions_list,  # Список регіонів (бокове меню)
#             "seasons": seasons_region,  # Список цьогорічних турнірів
#             # "matches": matches,
#             # "standings": standings,
#         },
#     )


@router.get("/{match_id}", response_model=schemas.MatchSchemas)
def read_match(match_id: int, db: Session = Depends(get_db)):
    db_match = crud.get_match(db, match_id=match_id)
    if db_match is None:
        raise HTTPException(status_code=404, detail="Match not found")
    return db_match


@router.put("/{match_id}", response_model=schemas.MatchSchemas)
def update_match(
    match_id: int,
    match: schemas.MatchUpdateSchemas,
    db: Session = Depends(get_db),
):
    db_match = crud.update_match(db=db, match_id=match_id, match=match)
    if db_match is None:
        raise HTTPException(status_code=404, detail="Match not found")
    return db_match


@router.delete("/{match_id}", response_model=schemas.MatchSchemas)
def delete_match(match_id: int, db: Session = Depends(get_db)):
    db_match = crud.delete_match(db=db, match_id=match_id)
    if db_match is None:
        raise HTTPException(status_code=404, detail="Match not found")
    return db_match
