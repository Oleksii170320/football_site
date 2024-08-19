from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from core.templating import templates

from core.database import get_db
from services import match as crud, region, standings as table
from services.match import (
    get_matches_results_season,
    get_matches_upcoming_season,
    get_match_info,
)
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
        "matches/matches.html",
        {
            "request": request,
            "news_list": news_list,  # Стрічка новин (всі регіони)
            "regions_list": regions_list,  # Список регіонів (бокове меню)
            "matches": matches,
        },
    )


# @router.get("/{match_id}", response_model=schemas.MatchSchemas)
# def read_match(request: Request, match_id: int, db: Session = Depends(get_db)):
#
#     news_list = get_news_list(db)
#     regions_list = get_regions_list(db)
#     # match = crud.get_match(db, match_id=match_id)
#     # match_info = get_match_info(db, match_id=match_id)
#
#     # if match is None:
#     #     raise HTTPException(status_code=404, detail="Match not found")
#     return templates.TemplateResponse(
#         "matches/match.html",
#         {
#             "request": request,
#             "news_list": news_list,  # Стрічка новин (всі регіони)
#             "regions_list": regions_list,  # Список регіонів (бокове меню)
#             # "match": match,
#             # "match_info": match_info,
#         },
#     )


@router.get("/{match_id}", response_model=schemas.MatchSchemas)
def read_match(request: Request, match_id: int, db: Session = Depends(get_db)):

    regions_list = get_regions_list(db)
    match = crud.get_match(db, match_id=match_id)
    match_info = get_match_info(db, match_id=match_id)

    if match is None:
        raise HTTPException(status_code=404, detail="Match not found")
    return templates.TemplateResponse(
        "matches/match.html",
        {
            "request": request,
            "regions_list": regions_list,  # Список регіонів (бокове меню)
            "match": match,
            "match_info": match_info,
        },
    )


@router.post("/", response_model=schemas.MatchSchemas)
def create_match(match: schemas.MatchCreateSchemas, db: Session = Depends(get_db)):
    return crud.create_match(db=db, match=match)


@router.get("/test", response_model=List[schemas.MatchSchemas])
def read_matches_test(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    matches = crud.get_matches(db, skip=skip, limit=limit)
    return matches


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
