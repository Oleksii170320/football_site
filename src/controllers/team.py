from datetime import datetime

import aiofiles

from fastapi import APIRouter, Depends, HTTPException, Request, Form, File, UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from typing import List, Optional
from pathlib import Path

from config import UPLOAD_DIR_FOR_LOGO
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
from services.team import get_team_staff, get_team, get_teams_in_season
from validation import team as schemas

router = APIRouter()


@router.get("/")
async def read_teams_all(request: Request, db: AsyncSession = Depends(get_db)):
    """Відкриває список всіх команд асинхронно"""

    return templates.TemplateResponse(
        "team/teams.html",
        {
            "request": request,
            "news_list": await get_news_list(db),  # Стрічка новин (всі регіони),
            "regions_list": await get_regions_list(db),
            "teams": await crud.get_teams(db),  # Отримання команд,
        },
    )


@router.get("/{team_slug}")
async def read_team_by_id(
    request: Request,
    team_slug: str,
    db: AsyncSession = Depends(get_db),
    region_slug=None,
):
    """Відкриває сторінку команди по ІД"""

    return templates.TemplateResponse(
        "team/team.html",
        {
            "request": request,
            "regions_list": await get_regions_list(db),
            "seasons": await get_seasons_region(db, region_slug=region_slug),
            "team": await get_team(db, team_slug=team_slug),
        },
    )


@router.get("/{team_id}/matches")
async def team_matches(
    request: Request, team_id: int, db: Session = Depends(get_db), region_slug=None
):
    """Відкриває всі матчі даної комсанди"""

    return templates.TemplateResponse(
        "team/team.html",
        {
            "request": request,
            "regions_list": await get_regions_list(db),  # Список регіонів (бокове меню)
            "seasons": await get_seasons_region(
                db, region_slug=region_slug
            ),  # Список цьогорічних турнірів
            "team": await crud.get_team(
                db, team_id=team_id
            ),  # Загальна інформація команди
            "matches": await get_matches_team(db, team_id=team_id),
        },
    )


@router.get("/{team_slug}/application")
async def team_application(
    request: Request, team_slug: str, db: Session = Depends(get_db), region_slug=None
):
    """Відкриває заявку гравців даної команди"""

    return templates.TemplateResponse(
        "team/team.html",
        {
            "request": request,
            "regions_list": await get_regions_list(db),  # Список регіонів (бокове меню)
            "seasons": await get_seasons_region(
                db, region_slug=region_slug
            ),  # Список цьогорічних турнірів
            "team": await crud.get_team(
                db, team_slug=team_slug
            ),  # Загальна інформація команди
            "application": await get_team_staff(db, team_slug=team_slug),
        },
    )


@router.get("/{team_slug}/leadership")
async def team_leadership(
    request: Request, team_slug: str, db: Session = Depends(get_db), region_slug=None
):
    """Керівництво команди"""

    return templates.TemplateResponse(
        "team/team.html",
        {
            "request": request,
            "regions_list": await get_regions_list(db),  # Список регіонів (бокове меню)
            "seasons": await get_seasons_region(db, region_slug=region_slug),
            "team": await crud.get_team(
                db, team_slug=team_slug
            ),  # Загальна інформація команди
            "leadership": await get_team_staff(db, team_slug=team_slug),
        },
    )


@router.get("/{team_slug}/achievement")
async def team_achievement(
    request: Request, team_slug: str, db: Session = Depends(get_db), region_slug=None
):
    """Історія досягнення команди"""

    return templates.TemplateResponse(
        "team/team.html",
        {
            "request": request,
            "regions_list": await get_regions_list(db),  # Список регіонів (бокове меню)
            "seasons": await get_seasons_region(db, region_slug=region_slug),
            "team": await crud.get_team(db, team_slug=team_slug),
            "achievement": await get_seasons_winner(db, team_slug=team_slug),
        },
    )


@router.get("/{team_slug}/history")
async def read_team_history(
    request: Request, team_slug: str, db: Session = Depends(get_db), region_slug=None
):
    """Історія виступів команди в турнірах"""

    return templates.TemplateResponse(
        "team/team.html",
        {
            "request": request,
            "regions_list": await get_regions_list(db),  # Список регіонів (бокове меню)
            "seasons": await get_seasons_region(db, region_slug=region_slug),
            "team": await crud.get_team(db, team_slug=team_slug),
            "history": await get_seasons_teams_history(db, team_slug=team_slug),
        },
    )


@router.get("/{team_id}/history")
async def read_team_history(
    request: Request,
    team_id: int,
    db: AsyncSession = Depends(get_db),
    region_slug: Optional[str] = None,
):
    """Історія виступів команди в турнірах"""

    return templates.TemplateResponse(
        "team/team.html",
        {
            "request": request,
            "regions_list": await get_regions_list(db),
            "seasons": await get_seasons_region(db, region_slug=region_slug),
            "team": await crud.get_team(db, team_id=team_id),
            "history": await get_seasons_teams_history(db, team_id=team_id),
        },
    )


@router.post("/", response_model=schemas.TeamSchemas)
async def create_team(
    team: schemas.TeamCreateSchemas, db: AsyncSession = Depends(get_db)
):
    return await crud.create_team(db=db, team=team)


@router.post("/new_team", response_model=schemas.TeamSchemas)
async def create_team(
    name: str = Form(...),
    city: str = Form(...),
    region_id: int = Form(...),
    full_name: Optional[str] = Form(None),
    slug: str = Form(...),
    foundation_year: Optional[str] = Form(None),
    clubs_site: Optional[str] = Form(None),
    stadium_id: Optional[int] = Form(0),
    president_id: Optional[int] = Form(0),
    coach_id: Optional[int] = Form(0),
    logo: Optional[str] = Form(None),
    # logo: UploadFile = File(...),  # У разі додавання файлів
    description: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db),  # Використання асинхронної сесії
):
    # Створюємо об'єкт для команди на основі отриманих даних
    db_team = schemas.TeamCreateSchemas(
        name=name,
        city=city,
        region_id=region_id,
        full_name=full_name,
        slug=slug,
        foundation_year=foundation_year,
        clubs_site=clubs_site,
        stadium_id=stadium_id,
        president_id=president_id,
        coach_id=coach_id,
        logo=logo,
        description=description,
    )

    # Викликаємо асинхронний CRUD для створення команди
    return await crud.create_team(db=db, team=db_team)


# @router.post("/upload_logo")
# async def upload_logo(
#     file: UploadFile = File(...),
#     region_slug: str = Form(...),
#     team_slug: str = Form(...),
#     db: AsyncSession = Depends(get_db),
# ):
#     # Перевірка розширення файлу
#     file_extension = file.filename.split(".")[-1].lower()
#     if file_extension not in ["png", "jpg", "jpeg"]:
#         raise HTTPException(
#             status_code=400,
#             detail="Недопустимий формат файлу. Дозволено лише png, jpg, jpeg.",
#         )
#
#     # Створення директорії, якщо її немає
#     dir_path = Path(UPLOAD_DIR_FOR_LOGO) / region_slug
#     dir_path.mkdir(parents=True, exist_ok=True)
#
#     # Формування нової назви файлу
#     current_date = datetime.now()
#     formatted_date = current_date.strftime("%S-%M-%H-%d-%m-%Y")
#     new_file_name = f"{region_slug}/{team_slug}_{formatted_date}.{file_extension}"
#     file_path = dir_path / new_file_name
#
#     # Збереження файлу
#     async with aiofiles.open(file_path, "wb") as buffer:
#         content = await file.read()
#         await buffer.write(content)
#
#     # Оновлення запису в БД з новим ім'ям файлу
#     try:
#         await crud.update_team_logo(db, team_slug, new_file_name)
#     except ValueError as e:
#         raise HTTPException(status_code=404, detail=str(e))
#
#     return JSONResponse(content={"filename": new_file_name})


@router.post("/upload_logo")
async def upload_logo(
    file: UploadFile = File(...),
    region_slug: str = Form(...),
    team_slug: str = Form(...),
    db: AsyncSession = Depends(get_db),
):
    # Перевірка розширення файлу
    file_extension = file.filename.split(".")[-1].lower()
    if file_extension not in ["png", "jpg", "jpeg", "jfif"]:
        raise HTTPException(
            status_code=400,
            detail="Недопустимий формат файлу. Дозволено лише png, jpg, jpeg.",
        )

    # Створення директорії, якщо її немає
    dir_path = Path(UPLOAD_DIR_FOR_LOGO) / region_slug
    dir_path.mkdir(parents=True, exist_ok=True)

    # Формування нової назви файлу
    current_date = datetime.now()
    formatted_date = current_date.strftime("%S-%M-%H-%d-%m-%Y")

    # Оновлена назва файлу без повторення region_slug
    new_file_name = f"{team_slug}_{formatted_date}.{file_extension}"
    file_path = dir_path / new_file_name

    # Збереження файлу
    async with aiofiles.open(file_path, "wb") as buffer:
        content = await file.read()
        await buffer.write(content)

    # Оновлення запису в БД з новим ім'ям файлу
    try:
        await crud.update_team_logo(db, team_slug, f"{region_slug}/{new_file_name}")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    print("Запит на завантаження логотипу прийнято")
    return JSONResponse(content={"filename": new_file_name})


@router.get("/test", response_model=List[schemas.TeamSchemas])
async def read_teams_test(
    skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)
):
    teams = await crud.get_teams(db, skip=skip, limit=limit)
    return teams


@router.put("/{team_id}", response_model=schemas.TeamSchemas)
async def update_team(
    team_id: int, team: schemas.TeamUpdateSchemas, db: AsyncSession = Depends(get_db)
):
    db_team = await crud.update_team(db=db, team_id=team_id, team=team)
    if db_team is None:
        raise HTTPException(status_code=404, detail="Team not found")
    return db_team


@router.delete("/{team_id}", response_model=schemas.TeamSchemas)
async def delete_team(team_id: int, db: AsyncSession = Depends(get_db)):
    db_team = await crud.delete_team(db=db, team_id=team_id)
    if db_team is None:
        raise HTTPException(status_code=404, detail="Team not found")
    return db_team
