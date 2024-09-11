from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from core.templating import templates

from core.database import get_db
from services import match as crud
from services.match import (
    get_match_statistics,
    get_match_event,
    get_match_replacement,
    get_replacement,
)
from services.news_list import get_news_list
from services.region import get_regions_list
from validation import match as schemas


router = APIRouter()


@router.get("/")
def all_matches_list(request: Request, db: Session = Depends(get_db)):
    """Виводить всі матчі"""

    return templates.TemplateResponse(
        "matches/matches.html",
        {
            "request": request,
            "news_list": get_news_list(db),  # Стрічка новин (всі регіони)
            "regions_list": get_regions_list(db),  # Список регіонів (бокове меню)
            "matches": crud.get_matches(db),
        },
    )


@router.get("/{match_id}")
def read_match(request: Request, match_id: int, db: Session = Depends(get_db)):
    """Виводить матч по ІД"""

    match = crud.get_match(db, match_id=match_id)

    if match is None:
        raise HTTPException(status_code=404, detail="Match not found")
    return templates.TemplateResponse(
        "matches/match.html",
        {
            "request": request,
            "regions_list": get_regions_list(db),  # Список регіонів (бокове меню)
            "match": match,
        },
    )


@router.get("/{match_id}/review")
def match_summary_review(
    request: Request, match_id: int, db: Session = Depends(get_db)
):
    """Виводить дані для огляду подій в матчі"""

    match = crud.get_match(db, match_id=match_id)
    if match is None:
        raise HTTPException(status_code=404, detail="Match not found")
    return templates.TemplateResponse(
        "matches/match.html",
        {
            "request": request,
            "regions_list": get_regions_list(db),  # Список регіонів (бокове меню)
            "match": match,  # Головна інформація про матч
            "events": get_match_event(db, match_id=match_id),
            "replacement": get_match_replacement(db, match_id=match_id),
        },
    )


@router.get("/{match_id}/lineups")
def match_summary_lineups(
    request: Request, match_id: int, db: Session = Depends(get_db)
):
    """Виводить склад команд в матчі"""

    match = crud.get_match(db, match_id=match_id)
    if match is None:
        raise HTTPException(status_code=404, detail="Match not found")
    return templates.TemplateResponse(
        "matches/match.html",
        {
            "request": request,
            "regions_list": get_regions_list(db),  # Список регіонів (бокове меню)
            "match": match,  # Головна інформація про матч
            "lineups": get_match_statistics(db, match_id=match_id),
            "replacements": get_replacement(db, match_id=match_id),
        },
    )


@router.get("/{match_id}/statistics")
def match_summary_statistics(
    request: Request, match_id: int, db: Session = Depends(get_db)
):
    """Виводить дані для статистики матчу"""

    match = crud.get_match(db, match_id=match_id)
    if match is None:
        raise HTTPException(status_code=404, detail="Match not found")
    return templates.TemplateResponse(
        "matches/match.html",
        {
            "request": request,
            "regions_list": get_regions_list(db),  # Список регіонів (бокове меню)
            "match": match,
            "statistics": [],
        },
    )


@router.post("/")
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
