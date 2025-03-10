from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from core.templating import render
from core.database import get_db
from helpers.authentications import get_current_user_for_button
from services import stadium as crud_stadium
from services.regions.region import get_regions_list
from services.stadium import get_stadium_teams
from validation import stadium as schemas

router = APIRouter()


@router.get("/search", response_model=List[schemas.StadiumSchemas])
async def search_stadiums_endpoint(query: str, db: AsyncSession = Depends(get_db)):
    """Пошук стадіонів за введеним запитом"""
    stadiums = await crud_stadium.get_search_stadiums(db=db, query=query)
    return stadiums


@router.get("/test", response_model=List[schemas.StadiumSchemas])
async def read_stadiums_test(
    skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db),
):
    stadiums = await crud_stadium.get_stadiums(db, skip=skip, limit=limit)
    return stadiums


@router.get("/", response_model=List[schemas.StadiumSchemas])
async def read_stadiums(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user_for_button),
):
    stadiums = await crud_stadium.get_stadiums(db, skip=skip, limit=limit)
    return render(
        "stadium/stadiums.html",
        request,
        {
            "stadiums": stadiums,
            "is_authenticated": is_authenticated,  # Передаємо значення
            "user_session": user_session,  # Ім'я користувача
        },
    )


@router.get("/{stadium_id}", response_model=schemas.StadiumSchemas)
async def read_stadium(
    request: Request, stadium_id: int, db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user_for_button),
):

    return render(
        "stadium/stadium.html",
        request,
        {
            "regions_list": await get_regions_list(db),  # Список регіонів (бокове меню)
            "taems": await get_stadium_teams(db, stadium_id=stadium_id),
            "stadium": await crud_stadium.get_stadium(db, stadium_id=stadium_id),
            "is_authenticated": is_authenticated,  # Передаємо значення
            "user_session": user_session,  # Ім'я користувача
        },
    )


@router.post("/", response_model=schemas.StadiumSchemas)
async def create_stadium(
    stadium: schemas.StadiumCreateSchemas, db: AsyncSession = Depends(get_db)
):
    return await crud_stadium.create_stadium(db=db, stadium=stadium)


@router.put("/{stadium_id}", response_model=schemas.StadiumSchemas)
async def update_stadium(
    stadium_id: int,
    stadium: schemas.StadiumUpdateSchemas,
    db: AsyncSession = Depends(get_db),
):
    db_stadium = await crud_stadium.update_stadium(
        db=db, stadium_id=stadium_id, stadium=stadium
    )
    if db_stadium is None:
        raise HTTPException(status_code=404, detail="Stadium not found")
    return db_stadium


@router.delete("/{stadium_id}", response_model=schemas.StadiumSchemas)
async def delete_stadium(stadium_id: int, db: AsyncSession = Depends(get_db)):
    db_stadium = await crud_stadium.delete_stadium(db=db, stadium_id=stadium_id)
    if db_stadium is None:
        raise HTTPException(status_code=404, detail="Stadium not found")
    return db_stadium
