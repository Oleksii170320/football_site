from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List

from core.templating import templates
from core.database import get_db
from services import season as crud

from services.region import get_regions_list
from services.season import (
    get_season_tournament,
)
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


@router.get("/archive/{tournament_id}", response_model=List[schemas.SeasonSchemas])
def read_seasons(
    request: Request,
    tournament_id: int,
    db: Session = Depends(get_db),
):

    regions_list = get_regions_list(db)
    seasons_archive = get_season_tournament(db, tournament_id=tournament_id)

    return templates.TemplateResponse(
        "season_archive.html",
        {
            "request": request,
            "regions_list": regions_list,  # Список регіонів (бокове меню)
            "seasons_archive": seasons_archive,
        },
    )


@router.post("/", response_model=schemas.SeasonSchemas)
def create_season(season: schemas.SeasonCreateSchemas, db: Session = Depends(get_db)):
    return crud.create_season(db=db, season=season)


@router.get("/test", response_model=List[schemas.SeasonSchemas])
def read_seasons_test(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    seasons = crud.get_seasons(db, skip=skip, limit=limit)
    return seasons


@router.get("/{season_id}", response_model=schemas.SeasonSchemas)
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


@router.post("/link/", response_model=schemas.SeasonSchemas)
def link_season_team(season_id: int, team_id: int, db: Session = Depends(get_db)):
    return crud.link_season_team(db, season_id=season_id, team_id=team_id)


# @router.post("/seasons/{season_id}/teams/{team_id}", response_model=schemas.SeasonSchemas)
# def add_team_to_group(db: Session, team_id: int, season_id: int):
#     team = db.query(Team).filter(Team.id == team_id).first()
#     season = db.query(Season).filter(Season.id == season_id).first()
#     if not team or not season:
#         raise HTTPException(status_code=404, detail="User or Group not found")
#     season.teams.append(team)
#     db.commit()
#     return team


# @router.post("/seasons/{season_id}/teams/{team_id}", response_model=schemas.SeasonSchemas)
# def add_team_to_group(user_id: int, group_id: int, db: Session = Depends(get_db)):
#     user = db.query(UserModel).filter(UserModel.id == user_id).first()
#     group = db.query(GroupModel).filter(GroupModel.id == group_id).first()
#     if not user or not group:
#         raise HTTPException(status_code=404, detail="User or Group not found")
#     user.groups.append(group)
#     db.commit()
#     return user
