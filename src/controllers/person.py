from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List

from core.templating import templates
from core.database import get_db
from models import Person
from services import person as crud
from services.position_role import get_persons_position_team
from services.region import get_regions_list
from validation import person as schemas


router = APIRouter()


@router.get("/", response_model=schemas.PersonSchemas)
def read_team(request: Request, db: Session = Depends(get_db)):

    regions_list = get_regions_list(db)
    persons = crud.get_persons(db)

    if persons is None:
        raise HTTPException(status_code=404, detail="Person not found")
    return templates.TemplateResponse(
        "persons/persons.html",
        {
            "request": request,
            "regions_list": regions_list,  # Список регіонів (бокове меню)
            "persons": persons,
        },
    )


@router.get("/{person_id}", response_model=schemas.PersonSchemas)
def read_team(request: Request, person_id: int, db: Session = Depends(get_db)):

    regions_list = get_regions_list(db)
    person = crud.get_person(db, person_id=person_id)
    positions_role = get_persons_position_team(db, person_id=person_id)

    if person is None:
        raise HTTPException(status_code=404, detail="Team not found")
    return templates.TemplateResponse(
        "persons/person.html",
        {
            "request": request,
            "regions_list": regions_list,  # Список регіонів (бокове меню)
            "person": person,
            "positions_role": positions_role,
        },
    )


@router.get("/{person_id}/club_career", response_model=schemas.PersonSchemas)
def read_team_career(request: Request, person_id: int, db: Session = Depends(get_db)):

    regions_list = get_regions_list(db)
    person = crud.get_person(db, person_id=person_id)
    positions_role = get_persons_position_team(db, person_id=person_id)
    playing_career = crud.get_person_team_career(db, person_id=person_id)

    if person is None:
        raise HTTPException(status_code=404, detail="Team not found")
    return templates.TemplateResponse(
        "persons/person.html",
        {
            "request": request,
            "regions_list": regions_list,  # Список регіонів (бокове меню)
            "person": person,
            "positions_role": positions_role,
            "club_career": playing_career,  # Список команд за які грав гравець
        },
    )


@router.get("/{person_id}/tournaments", response_model=schemas.PersonSchemas)
def read_team_applications(
    request: Request, person_id: int, db: Session = Depends(get_db)
):

    regions_list = get_regions_list(db)
    person = crud.get_person(db, person_id=person_id)
    positions_role = get_persons_position_team(db, person_id=person_id)
    tournaments = crud.get_person_teams_tournaments(db, person_id=person_id)

    if person is None:
        raise HTTPException(status_code=404, detail="Team not found")
    return templates.TemplateResponse(
        "persons/person.html",
        {
            "request": request,
            "regions_list": regions_list,  # Список регіонів (бокове меню)
            "person": person,
            "positions_role": positions_role,
            "tournaments": tournaments,  # Список Турнрірів, ву яких гралда команда
        },
    )


@router.get("/", response_model=List[schemas.PersonSchemas])
def read_regions(request: Request, db: Session = Depends(get_db)):
    """виводить список регіонів"""

    persons = crud.get_persons(db)

    return templates.TemplateResponse(
        "regions.html",
        {
            "request": request,
            "persons": persons,
        },
    )


# для додавання нової області
@router.post("/", response_model=schemas.PersonSchemas)
def create_person(person: schemas.PersonCreateSchemas, db: Session = Depends(get_db)):
    return crud.create_person(db=db, person=person)


# виводить список регіонів у swager
@router.get("/test", response_model=List[schemas.PersonSchemas])
def read_person_test(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    persons = crud.get_persons(db, skip=skip, limit=limit)
    return persons


@router.put("/{person_id}", response_model=schemas.PersonSchemas)
def update_person(
    person_id: int,
    person: schemas.PersonUpdateSchemas,
    db: Session = Depends(get_db),
):
    db_person = crud.update_person(db=db, person_id=person_id, person=person)
    if db_person is None:
        raise HTTPException(status_code=404, detail="Person not found")
    return db_person


@router.delete("/{person_id}", response_model=schemas.PersonSchemas)
def delete_person(person_id: int, db: Session = Depends(get_db)):
    db_person = crud.delete_person(db=db, person_id=person_id)
    if db_person is None:
        raise HTTPException(status_code=404, detail="Person not found")
    return db_person
