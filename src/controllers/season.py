from fastapi import APIRouter, Depends, HTTPException, status, Request, Form
from sqlalchemy.orm import Session
from typing import List, Optional

from starlette.responses import RedirectResponse, HTMLResponse, JSONResponse

from core.templating import templates
from core.database import get_db
from services import season as crud

from services.region import get_regions_list, get_regions
from services.season import (
    get_season_tournament,
)
from services.team import get_teams_in_season
from validation import season as schemas

router = APIRouter()


@router.get("/", response_model=List[schemas.SeasonSchemas])
def read_seasons(
    request: Request, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)
):

    seasons = crud.get_seasons(db, skip=skip, limit=limit)

    return templates.TemplateResponse(
        "seasons.html",
        {
            "request": request,
            "seasons": seasons,
        },
    )


@router.get("/archive/{tournament_id}")
def read_seasons(
    request: Request,
    tournament_id: int,
    db: Session = Depends(get_db),
):
    seasons_archive = get_season_tournament(db, tournament_id=tournament_id)

    return templates.TemplateResponse(
        "season_archive.html",
        {
            "request": request,
            "regions_list": get_regions_list(db),  # Список регіонів (бокове меню)
            "seasons_archive": seasons_archive,
        },
    )


@router.post("/")
def create_season(season: schemas.SeasonCreateSchemas, db: Session = Depends(get_db)):
    return crud.create_season(db=db, season=season)


@router.get("/test", response_model=List[schemas.SeasonSchemas])
def read_seasons_test(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    seasons = crud.get_seasons(db, skip=skip, limit=limit)
    return seasons


@router.get("/{season_slug}", response_model=schemas.SeasonSchemas)
def read_season(season_id: int, db: Session = Depends(get_db)):
    db_season = crud.get_season(db, season_id=season_id)
    if db_season is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Season not found"
        )
    return db_season


@router.put("/{season_id}", response_model=schemas.SeasonSchemas)
def update_season(
    season_id: int, season: schemas.SeasonUpdateSchemas, db: Session = Depends(get_db)
):
    db_season = crud.update_season(db=db, season_id=season_id, season=season)
    if db_season is None:
        raise HTTPException(status_code=404, detail="Season not found")
    return db_season


@router.delete("/{season_id}", response_model=schemas.SeasonSchemas)
def delete_season(season_id: int, db: Session = Depends(get_db)):
    db_season = crud.delete_season(db=db, season_id=season_id)
    if db_season is None:
        raise HTTPException(status_code=404, detail="Season not found")
    return db_season


# Нижче ендпоінти для робити з таблицею-медіатор (m2m) Команди-Сезон
@router.post("/link/", response_model=schemas.SeasonSchemas)
def link_season_team(season_id: int, team_id: int, db: Session = Depends(get_db)):
    return crud.link_season_team(db, season_id=season_id, team_id=team_id)


@router.post("/add_teams")
async def link_season_team(
    season_id: int = Form(...),
    team_id: int = Form(...),
    db: Session = Depends(get_db),
):
    try:
        crud.link_season_team(db, season_id=season_id, team_id=team_id)

        # Отримання оновленого списку команд
        teams = get_teams_in_season(db, season_slug=season_id)

        return JSONResponse(content={"status": "success", "teams": teams})
    except Exception as e:
        return JSONResponse(
            content={"status": "error", "message": str(e)}, status_code=500
        )


@router.delete("/del_teams/{season_id}/{team_id}")
def delete_season_team(season_id: int, team_id: int, db: Session = Depends(get_db)):
    db_season_team = crud.delete_season_team(
        db=db, season_id=season_id, team_id=team_id
    )

    if db_season_team is None:
        raise HTTPException(status_code=404, detail="Team or Season not found")

    return JSONResponse(
        content={"status": "success", "message": "Team removed from season"},
        status_code=200,
    )
