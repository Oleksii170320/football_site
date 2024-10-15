from fastapi import APIRouter, Depends, HTTPException, status, Request, Form
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from starlette.responses import JSONResponse, RedirectResponse

from core.templating import templates, render
from core.database import get_db
from models import TeamSeason
from services import season as crud, get_regions_list

from services.team import get_teams_for_id
from validation import season as schemas

router = APIRouter()


@router.get("/", response_model=List[schemas.SeasonSchemas])
async def read_seasons(
    request: Request, skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)
):

    return render(
        "seasons/season_list.html",
        request,
        {
            "regions_list": await get_regions_list(db),
            "seasons": await crud.get_seasons(db, skip=skip, limit=limit),
        },
    )


@router.get("/test", response_model=List[schemas.SeasonSchemas])
async def read_seasons_test(
    skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)
):
    seasons = await crud.get_seasons(db, skip=skip, limit=limit)
    return seasons


@router.get("/{season_slug}", response_model=schemas.SeasonSchemas)
async def read_season(season_slug: str, db: AsyncSession = Depends(get_db)):
    db_season = await crud.get_season(db, season_slug=season_slug)
    if db_season is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Season not found"
        )
    return db_season


@router.post("/", response_model=schemas.SeasonSchemas)
async def create_season(
    season: schemas.SeasonCreateSchemas, db: AsyncSession = Depends(get_db)
):
    return await crud.create_season(db=db, season=season)


@router.put("/{season_id}", response_model=schemas.SeasonSchemas)
async def update_season(
    season_id: int,
    season: schemas.SeasonUpdateSchemas,
    db: AsyncSession = Depends(get_db),
):
    db_season = await crud.update_season(db=db, season_id=season_id, season=season)
    if db_season is None:
        raise HTTPException(status_code=404, detail="Season not found")
    return db_season


@router.delete("/{season_id}", response_model=schemas.SeasonSchemas)
async def delete_season(season_id: int, db: AsyncSession = Depends(get_db)):
    db_season = await crud.delete_season(db=db, season_id=season_id)
    if db_season is None:
        raise HTTPException(status_code=404, detail="Season not found")
    return db_season


# Нижче ендпоінти для робити з таблицею-медіатор (m2m) Команди-Сезон
@router.post("/link/", response_model=schemas.SeasonSchemas)
async def link_season_team(
    season_id: int, team_id: int, db: AsyncSession = Depends(get_db)
):
    result = await crud.link_season_team(db, season_id=season_id, team_id=team_id)
    if not result:
        raise HTTPException(status_code=404, detail="Failed to link season and team")
    return result


import logging


# @router.post("/add_teams")
# async def link_season_team(
#     season_id: int = Form(...),
#     team_id: int = Form(...),
#     db: AsyncSession = Depends(get_db),
# ):
#     try:
#         await crud.link_season_team(db, season_id=season_id, team_id=team_id)
#         teams = await get_teams_for_id(db, season_id=season_id)
#         return JSONResponse(content={"status": "success", "teams": teams})
#     except Exception as e:
#         logging.exception("Error while linking team to season")
#         return JSONResponse(
#             content={"status": "error", "message": str(e)}, status_code=500
#         )


# @router.post("/add_teams")
# async def link_season_team(
#     season_id: int = Form(...),
#     team_id: int = Form(...),
#     db: AsyncSession = Depends(get_db),
# ):
#     try:
#         response = await crud.link_season_team(db, season_id=season_id, team_id=team_id)
#         teams = await get_teams_for_id(db, season_id=season_id)
#         return JSONResponse(content={"status": "success", "teams": teams})
#     except Exception as e:
#         logging.exception("Error while linking team to season")
#         return JSONResponse(
#             content={"status": "error", "message": str(e)}, status_code=500
#         )


# @router.post("/add_teams")
# async def add_team_to_season(
#     season_id: int = Form(...),
#     team_id: int = Form(...),
#     db: AsyncSession = Depends(get_db),
# ):
#     try:
#         await link_season_team(db, season_id, team_id)
#         return JSONResponse(
#             content={
#                 "status": "success",
#                 "message": "Команда успішно додана до сезону!",
#             }
#         )
#     except HTTPException as e:
#         return JSONResponse(
#             content={"status": "error", "message": str(e.detail)},
#             status_code=e.status_code,
#         )
#     except Exception as e:
#         return JSONResponse(
#             content={"status": "error", "message": "Щось пішло не так!"},
#             status_code=500,
#         )


import logging


@router.post("/add_teams")
async def add_team_to_season(
    season_id: int = Form(...),
    team_id: int = Form(...),
    db: AsyncSession = Depends(get_db),
):
    logging.info(f"Received season_id: {season_id}, team_id: {team_id}")
    try:
        logging.info(f"Attempting to link season {season_id} with team {team_id}")

        # Виклик функції, яка пов'язує сезон з командою
        await crud.link_season_team(db, season_id, team_id)

        logging.info("Team successfully linked to the season")

        return JSONResponse(
            content={
                "status": "success",
                "message": "Команда успішно додана до сезону!",
            }
        )
    except HTTPException as e:
        logging.error(f"HTTPException: {e.detail}")
        return JSONResponse(
            content={"status": "error", "message": str(e.detail)},
            status_code=e.status_code,
        )
    except Exception as e:
        logging.error(f"Exception: {str(e)}")
        return JSONResponse(
            content={"status": "error", "message": "Щось пішло не так!"},
            status_code=500,
        )


@router.delete("/del_teams/{season_id}/{team_id}")
async def delete_season_team(
    season_id: int, team_id: int, db: AsyncSession = Depends(get_db)
):
    db_season_team = await crud.delete_season_team(
        db=db, season_id=season_id, team_id=team_id
    )

    if db_season_team is None:
        raise HTTPException(status_code=404, detail="Team or Season not found")

    return JSONResponse(
        content={"status": "success", "message": "Team removed from season"},
        status_code=200,
    )
