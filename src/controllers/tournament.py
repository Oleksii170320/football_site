from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List

from core.templating import templates
from core.database import get_db
from services import tournament as crud
from services.news_list import get_news_list
from services.region import get_regions_list
from services.tournament import get_tournament_slug, get_tournament_archive
from validation import tournament as schemas


router = APIRouter()


@router.get("/", response_model=List[schemas.TournamentSchemas])
def read_all_tournaments(
    request: Request, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    """Відкриває список всіх турнірів"""

    return templates.TemplateResponse(
        "tournaments.html",
        {
            "request": request,
            "news_list": get_news_list(db),  # Стрічка новин (всі регіони)
            "regions_list": get_regions_list(db),  # Список регіонів (бокове меню)
            "tournaments": crud.get_tournaments(db, skip=skip, limit=limit),
        },
    )


@router.get("/{tournament_slug}", response_model=List[schemas.TournamentSchemas])
def get_tournament_by_slug(
    request: Request, tournament_slug: str, db: Session = Depends(get_db)
):
    """Відкриває сторынку турныру по SLUG"""

    return templates.TemplateResponse(
        "tournament/tournament.html",
        {
            "request": request,
            "regions_list": get_regions_list(db),  # Список регіонів (бокове меню)
            "tournaments": get_tournament_slug(db, tournament_slug=tournament_slug),
            "seasons_archive": get_tournament_archive(
                db, tournament_slug=tournament_slug
            ),
        },
    )


@router.get("/{tournament_id}", response_model=schemas.TournamentSchemas)
def read_tournament_by_id(tournament_id: int, db: Session = Depends(get_db)):
    """Відкриває сторынку турныру по ІД"""

    db_tournament = crud.get_tournament(db, tournament_id=tournament_id)
    if db_tournament is None:
        raise HTTPException(status_code=404, detail="Tournament not found")
    return db_tournament


@router.post("/", response_model=schemas.TournamentSchemas)
def create_tournament(
    tournament: schemas.TournamentCreateSchemas, db: Session = Depends(get_db)
):
    return crud.create_tournament(db=db, tournament=tournament)


@router.get("/test", response_model=List[schemas.TournamentSchemas])
def read_tournaments_test(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    tournaments = crud.get_tournaments(db, skip=skip, limit=limit)
    return tournaments


@router.put("/{tournament_id}", response_model=schemas.TournamentSchemas)
def update_tournament(
    tournament_id: int,
    tournament: schemas.TournamentUpdateSchemas,
    db: Session = Depends(get_db),
):
    db_tournament = crud.update_tournament(
        db=db, tournament_id=tournament_id, tournament=tournament
    )
    if db_tournament is None:
        raise HTTPException(status_code=404, detail="Tournament not found")
    return db_tournament


@router.delete("/{tournament_id}", response_model=schemas.TournamentSchemas)
def delete_tournament(tournament_id: int, db: Session = Depends(get_db)):
    db_tournament = crud.delete_tournament(db=db, tournament_id=tournament_id)
    if db_tournament is None:
        raise HTTPException(status_code=404, detail="Tournament not found")
    return db_tournament
