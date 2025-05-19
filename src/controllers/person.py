from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from typing import List

from starlette.responses import HTMLResponse

from core.templating import render
from core.database import get_db
from services import person as crud
from services.position_role import get_persons_position_team
from services.regions.region import get_regions_list
from validation import person as schemas


router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def persons_list(request: Request, db: AsyncSession = Depends(get_db)):
    """Дані для сторінки всіх персон на сайті"""

    return render(
        "persons/persons.html",
        {
            "request": request,
            "regions_list": await get_regions_list(db),
            "persons": await crud.get_persons(db),
        },
    )


@router.get("/{person_id}")
async def read_person(
    request: Request, person_id: int, db: AsyncSession = Depends(get_db)
):
    """Дані для сторінки персони по ІД"""

    return render(
        "persons/person.html",
        request,
        {
            "regions_list": await get_regions_list(db),  # Список регіонів (бокове меню)
            "person": await crud.get_person(db, person_id=person_id),
            "positions_role": await get_persons_position_team(db, person_id=person_id),
        },
    )


@router.get("/{person_id}/matches")
async def persons_club_career(
    request: Request, person_id: int, db: AsyncSession = Depends(get_db)
):
    """Інформація про матчі, в якіх грав гарець"""

    return render(
        "persons/person.html",
        request,
        {
            "regions_list": await get_regions_list(db),  # Список регіонів (бокове меню)
            "person": await crud.get_person(db, person_id=person_id),
            "positions_role": await get_persons_position_team(db, person_id=person_id),
            "matches": await crud.get_person_matches(db, person_id=person_id),
        },
    )


@router.get("/{person_id}/club_career")
async def persons_club_career(
    request: Request, person_id: int, db: AsyncSession = Depends(get_db)
):
    """Інформація футбольної кар'єри гравця"""

    return render(
        "persons/person.html",
        request,
        {
            "regions_list": await get_regions_list(db),  # Список регіонів (бокове меню)
            "person": await crud.get_person(db, person_id=person_id),
            "positions_role": await get_persons_position_team(db, person_id=person_id),
            "club_career": await crud.get_person_team_career(db, person_id=person_id),
        },
    )


@router.get("/{person_id}/tournaments")
async def persons_tournaments(
    request: Request, person_id: int, db: AsyncSession = Depends(get_db)
):
    """Інформація про турніри, в яких грав гравець"""

    return render(
        "persons/person.html",
        request,
        {
            "regions_list": await get_regions_list(db),  # Список регіонів (бокове меню)
            "person": await crud.get_person(db, person_id=person_id),
            "positions_role": await get_persons_position_team(db, person_id=person_id),
            "tournaments": await crud.get_person_teams_tournaments(
                db, person_id=person_id
            ),
        },
    )


# для додавання нової області
@router.post("/", response_model=schemas.PersonSchemas)
def create_person(person: schemas.PersonCreateSchemas, db: Session = Depends(get_db)):
    return crud.create_person(db=db, person=person)


# виводить список регіонів у swager
@router.get("/test", response_model=List[schemas.PersonSchemas])
async def read_person_test(
    skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)
):
    persons = await crud.get_persons(db, skip=skip, limit=limit)
    return persons


@router.put("/{person_id}", response_model=schemas.PersonSchemas)
async def update_person(
    person_id: int,
    person: schemas.PersonUpdateSchemas,
    db: AsyncSession = Depends(get_db),
):
    db_person = await crud.update_person(db=db, person_id=person_id, person=person)
    if db_person is None:
        raise HTTPException(status_code=404, detail="Person not found")
    return db_person


@router.delete("/{person_id}", response_model=schemas.PersonSchemas)
async def delete_person(
    person_id: int,
    db: AsyncSession = Depends(get_db),
):
    db_person = await crud.delete_person(db=db, person_id=person_id)
    if db_person is None:
        raise HTTPException(status_code=404, detail="Person not found")
    return db_person
