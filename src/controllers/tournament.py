from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from core.templating import render
from core.database import get_db
from helpers.authentications import (
    get_current_user_for_button,
)
from services import tournament as crud
from services.news_list import get_news_list
from services.regions.region import get_regions_list
from services.tournament import get_tournament_slug, get_tournament_archive
from validation import tournament as schemas


router = APIRouter()


@router.get("/")
async def read_all_tournaments(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user_for_button),
):
    """Відкриває список всіх турнірів"""

    user_session, is_authenticated = current_user

    return render(
        "tournaments.html",
        request,
        {
            "news_list": await get_news_list(db),  # Стрічка новин (всі регіони)
            "regions_list": await get_regions_list(db),  # Список регіонів (бокове меню)
            "tournaments": await crud.get_tournaments(db, skip=skip, limit=limit),
            "is_authenticated": is_authenticated,  # Передаємо значення
            "user_session": user_session,  # Ім'я користувача
        },
    )


@router.get("/{tournament_slug}")
async def get_tournament_by_slug(
    request: Request,
    tournament_slug: str,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user_for_button),
):
    """Відкриває сторінку турніру по SLUG"""

    user_session, is_authenticated = current_user

    return render(
        "tournament/tournament.html",
        request,
        {
            "regions_list": await get_regions_list(db),
            "tournaments": await get_tournament_slug(db, tournament_slug),
            "seasons_archive": await get_tournament_archive(db, tournament_slug),
            "is_authenticated": is_authenticated,  # Передаємо значення
            "user_session": user_session,  # Ім'я користувача
        },
    )


@router.get("/{tournament_slug}/new_season")
async def get_tournament_by_slug(
    request: Request,
    tournament_slug: str,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user_for_button),
):
    """Відкриває сторінку турніру по SLUG"""

    user_session, is_authenticated = current_user

    return render(
        "tournament/tournament.html",
        request,
        {
            "regions_list": await get_regions_list(db),  # Список регіонів (бокове меню)
            "tournaments": await get_tournament_slug(
                db, tournament_slug=tournament_slug
            ),
            "seasons_archive": await get_tournament_archive(
                db, tournament_slug=tournament_slug
            ),
            "form": True,
            "is_authenticated": is_authenticated,  # Передаємо значення
            "user_session": user_session,  # Ім'я користувача
        },
    )


# @router.get("/{tournament_id}", response_model=schemas.TournamentSchemas)
# def read_tournament_by_id(tournament_id: int, db: Session = Depends(get_db)):
#     """Відкриває сторынку турныру по ІД"""
#
#     db_tournament = crud.get_tournament(db, tournament_id=tournament_id)
#     if db_tournament is None:
#         raise HTTPException(status_code=404, detail="Tournament not found")
#     return db_tournament


# @router.post("/", response_model=schemas.TournamentSchemas)
# def create_tournament(tournament: schemas.TournamentCreateSchemas, db: Session = Depends(get_db)):
#     return crud.create_tournament(db=db, tournament=tournament)


@router.post("/", response_model=schemas.TournamentSchemas)
async def create_tournament(
    tournament: schemas.TournamentCreateSchemas, db: AsyncSession = Depends(get_db)
):
    return await crud.create_tournament(db=db, tournament=tournament)


@router.put("/{tournament_id}", response_model=schemas.TournamentSchemas)
async def update_tournament(
    tournament_id: int,
    tournament: schemas.TournamentUpdateSchemas,
    db: AsyncSession = Depends(get_db),
):
    db_tournament = await crud.update_tournament(
        db=db, tournament_id=tournament_id, tournament=tournament
    )
    if db_tournament is None:
        raise HTTPException(status_code=404, detail="Tournament not found")
    return db_tournament


@router.delete("/{tournament_id}", response_model=schemas.TournamentSchemas)
async def delete_tournament(
    tournament_id: int,
    db: AsyncSession = Depends(get_db),
):
    db_tournament = await crud.delete_tournament(db=db, tournament_id=tournament_id)
    if db_tournament is None:
        raise HTTPException(status_code=404, detail="Tournament not found")
    return db_tournament
