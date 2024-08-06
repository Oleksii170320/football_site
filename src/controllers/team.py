from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List

from core.templating import templates
from core.database import get_db
from services import team as crud
from services.match import get_matches_team
from services.news_list import get_news_list
from services.region import get_regions_list
from services.season import (
    get_seasons_region,
    get_seasons_winner,
    get_seasons_teams_history,
)
from validation import team as schemas

router = APIRouter()


@router.get("/", response_model=List[schemas.TeamSchemas])
def read_teams(request: Request, db: Session = Depends(get_db)):

    news_list = get_news_list(db)
    regions_list = get_regions_list(db)
    teams = crud.get_teams(db)

    return templates.TemplateResponse(
        "teams.html",
        {
            "request": request,
            "news_list": news_list,  # Стрічка новин (всі регіони)
            "regions_list": regions_list,  # Список регіонів (бокове меню)
            "teams": teams,
        },
    )


@router.post("/", response_model=schemas.TeamSchemas)
def create_team(team: schemas.TeamCreateSchemas, db: Session = Depends(get_db)):
    return crud.create_team(db=db, team=team)


@router.get("/test", response_model=List[schemas.TeamSchemas])
def read_teams_test(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    teams = crud.get_teams(db, skip=skip, limit=limit)
    return teams


@router.get("/{team_id}", response_model=schemas.TeamSchemas)
def read_team(
    request: Request, team_id: int, db: Session = Depends(get_db), region_slug=None
):

    regions_list = get_regions_list(db)
    seasons_region = get_seasons_region(db, region_slug=region_slug)
    team = crud.get_team(db, team_id=team_id)

    if team is None:
        raise HTTPException(status_code=404, detail="Team not found")
    return templates.TemplateResponse(
        "team/team.html",
        {
            "request": request,
            "regions_list": regions_list,  # Список регіонів (бокове меню)
            "seasons": seasons_region,  # Список цьогорічних турнірів
            "team": team,
        },
    )


@router.get("/{team_id}/matches", response_model=schemas.TeamSchemas)
def read_team(
    request: Request, team_id: int, db: Session = Depends(get_db), region_slug=None
):

    regions_list = get_regions_list(db)
    seasons_region = get_seasons_region(db, region_slug=region_slug)
    team = crud.get_team(db, team_id=team_id)
    matches = get_matches_team(db, team_id=team_id)

    if team is None:
        raise HTTPException(status_code=404, detail="Team not found")
    return templates.TemplateResponse(
        "team/team.html",
        {
            "request": request,
            "regions_list": regions_list,  # Список регіонів (бокове меню)
            "seasons": seasons_region,  # Список цьогорічних турнірів
            "team": team,
            "matches": matches,
        },
    )


@router.get("/{team_id}/achievement", response_model=schemas.TeamSchemas)
def read_team(
    request: Request, team_id: int, db: Session = Depends(get_db), region_slug=None
):

    regions_list = get_regions_list(db)
    seasons_region = get_seasons_region(db, region_slug=region_slug)
    team = crud.get_team(db, team_id=team_id)
    achievement = get_seasons_winner(db, team_id=team_id)

    if team is None:
        raise HTTPException(status_code=404, detail="Team not found")
    return templates.TemplateResponse(
        "team/team.html",
        {
            "request": request,
            "regions_list": regions_list,  # Список регіонів (бокове меню)
            "seasons": seasons_region,  # Список цьогорічних турнірів
            "team": team,
            "achievement": achievement,
        },
    )


@router.get("/{team_id}/history", response_model=schemas.TeamSchemas)
def read_team(
    request: Request, team_id: int, db: Session = Depends(get_db), region_slug=None
):

    regions_list = get_regions_list(db)
    seasons_region = get_seasons_region(db, region_slug=region_slug)
    team = crud.get_team(db, team_id=team_id)
    history = get_seasons_teams_history(db, team_id=team_id)

    if team is None:
        raise HTTPException(status_code=404, detail="Team not found")

    return templates.TemplateResponse(
        "team/team.html",
        {
            "request": request,
            "regions_list": regions_list,  # Список регіонів (бокове меню)
            "seasons": seasons_region,  # Список цьогорічних турнірів
            "team": team,  # інформація про команду
            "history": history,  # Історія турнірів
        },
    )


@router.get("/{team_slug}", response_model=schemas.TeamSchemas)
def read_team(
    request: Request, team_slug: str, db: Session = Depends(get_db), region_slug=None
):

    regions_list = get_regions_list(db)
    team = crud.get_team_for_slug(db, team_slug=team_slug)

    if team is None:
        raise HTTPException(status_code=404, detail="Team not found")
    return templates.TemplateResponse(
        "team.html",
        {
            "request": request,
            "regions_list": regions_list,  # Список регіонів (бокове меню)
            "team": team,
        },
    )


@router.put("/{team_id}", response_model=schemas.TeamSchemas)
def update_team(
    team_id: int, team: schemas.TeamUpdateSchemas, db: Session = Depends(get_db)
):
    db_team = crud.update_team(db=db, team_id=team_id, team=team)
    if db_team is None:
        raise HTTPException(status_code=404, detail="Team not found")
    return db_team


@router.delete("/{team_id}", response_model=schemas.TeamSchemas)
def delete_team(team_id: int, db: Session = Depends(get_db)):
    db_team = crud.delete_team(db=db, team_id=team_id)
    if db_team is None:
        raise HTTPException(status_code=404, detail="Team not found")
    return db_team
