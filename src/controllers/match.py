from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from core.templating import render

from core.database import get_db
from services.matches import matches_crud as crud
from services.matches.match import (
    get_match,
    get_matches_all_information,
    get_match_statistics,
    get_match_event,
    get_replacement,
)
from services.news_list import get_news_list
from services.regions.region import get_regions_list
from validation import match as schemas


router = APIRouter()


@router.get("/")
async def all_matches_list(request: Request, db: AsyncSession = Depends(get_db)):
    """Виводить всі матчі"""

    return render(
        "matches/matches.html",
        request,
        {
            "news_list": await get_news_list(db),  # Стрічка новин (всі регіони)
            "regions_list": await get_regions_list(db),  # Список регіонів (бокове меню)
            "matches": await get_matches_all_information(db),
        },
    )


@router.get("/{match_id}")
async def read_match(
    request: Request, match_id: int, db: AsyncSession = Depends(get_db)
):
    """Виводить матч по ІД"""

    return render(
        "matches/match.html",
        request,
        {
            "regions_list": await get_regions_list(db),  # Список регіонів (бокове меню)
            "match": await get_match(db, match_id=match_id),
        },
    )


@router.get("/{match_id}/review")
async def match_summary_review(
    request: Request, match_id: int, db: AsyncSession = Depends(get_db)
):
    """Виводить дані для огляду подій в матчі"""

    return render(
        "matches/match.html",
        request,
        {
            "regions_list": await get_regions_list(db),  # Список регіонів (бокове меню)
            "match": await get_match(db, match_id=match_id),
            "events": await get_match_event(db, match_id=match_id),
        },
    )


@router.get("/{match_id}/lineups")
async def match_summary_lineups(
    request: Request, match_id: int, db: AsyncSession = Depends(get_db)
):
    """Виводить склад команд в матчі"""

    return render(
        "matches/match.html",
        request,
        {
            "regions_list": await get_regions_list(db),  # Список регіонів (бокове меню)
            "match": await get_match(db, match_id=match_id),
            "lineups": await get_match_statistics(db, match_id=match_id),
            "replacements": await get_replacement(db, match_id=match_id),
        },
    )


# @router.post("/new_match")
# async def create_match(
#     match: schemas.MatchCreateSchemas, db: AsyncSession = Depends(get_db)
# ):
#     return await crud.create_match(db=db, match=match)


from typing import Optional
from fastapi import Form


class MatchCreateForm:
    def __init__(
        self,
        event_epoch: Optional[int] = Form(None),
        season_id: int = Form(...),
        group_id: Optional[int] = Form(None),
        stage_id: Optional[int] = Form(None),
        round_id: Optional[int] = Form(None),
        stadium_id: Optional[int] = Form(None),
        team1_id: int = Form(...),
        team1_goals: Optional[int] = Form(None),
        team2_goals: Optional[int] = Form(None),
        team2_id: int = Form(...),
        team1_penalty: Optional[int] = Form(None),
        team2_penalty: Optional[int] = Form(None),
        status: str = Form(
            ...
        ),  # Замість MatchStatus, оскільки це потрібно конвертувати з форми
        standing: bool = Form(True),
        # Додаємо поля region_slug та season_slug
        region_slug: str = Form(...),
        season_slug: str = Form(...),
    ):
        self.event_epoch = event_epoch
        self.season_id = season_id
        self.group_id = group_id
        self.stage_id = stage_id
        self.round_id = round_id
        self.stadium_id = stadium_id
        self.team1_id = team1_id
        self.team1_goals = team1_goals
        self.team2_goals = team2_goals
        self.team2_id = team2_id
        self.team1_penalty = team1_penalty
        self.team2_penalty = team2_penalty
        self.status = status
        self.standing = standing
        self.region_slug = region_slug  # Нове поле
        self.season_slug = season_slug  # Нове поле


@router.post("/new_match")
async def create_match(
    match_form: MatchCreateForm = Depends(), db: AsyncSession = Depends(get_db)
):
    match_data = {
        "event": match_form.event_epoch,
        "season_id": match_form.season_id,
        "group_id": match_form.group_id,
        "stage_id": match_form.stage_id,
        "round_id": match_form.round_id,
        "stadium_id": match_form.stadium_id,
        "team1_id": match_form.team1_id,
        "team1_goals": match_form.team1_goals,
        "team2_goals": match_form.team2_goals,
        "team2_id": match_form.team2_id,
        "team1_penalty": match_form.team1_penalty,
        "team2_penalty": match_form.team2_penalty,
        "status": match_form.status,
        "standing": match_form.standing,
        "region_slug": match_form.region_slug,
        "season_slug": match_form.season_slug,
    }

    try:
        match = schemas.MatchCreateSchemas(**match_data)
        await create_match(db=db, match=match)
        return {
            "success": True,
            "region_slug": match_form.region_slug,
            "season_slug": match_form.season_slug,
        }
    except ValidationError as e:
        return {"success": False, "error": e.errors()}


@router.post("/")
async def create_match(
    match: schemas.MatchCreateSchemas, db: AsyncSession = Depends(get_db)
):
    return await crud.create_match(db=db, match=match)


@router.get("/test", response_model=List[schemas.MatchSchemas])
async def read_matches_test(
    skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)
):
    matches = await get_matches_all_information(db, skip=skip, limit=limit)
    return matches


@router.put("/{match_id}", response_model=schemas.MatchSchemas)
async def update_match(
    match_id: int,
    match: schemas.MatchUpdateSchemas,
    db: AsyncSession = Depends(get_db),
):
    db_match = await crud.update_match(db=db, match_id=match_id, match=match)
    if db_match is None:
        raise HTTPException(status_code=404, detail="Match not found")
    return db_match


@router.delete("/{match_id}", response_model=schemas.MatchSchemas)
async def delete_match(match_id: int, db: AsyncSession = Depends(get_db)):
    db_match = await crud.delete_match(db=db, match_id=match_id)
    if db_match is None:
        raise HTTPException(status_code=404, detail="Match not found")
    return db_match
