import enum

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List

from core.templating import templates
from core.database import get_db
from services import stadium as crud_stadium
from validation import stadium as schemas

router = APIRouter()


@router.post("/", response_model=schemas.StadiumSchemas)
def create_stadium(
    stadium: schemas.StadiumCreateSchemas, db: Session = Depends(get_db)
):
    return crud_stadium.create_stadium(db=db, stadium=stadium)


@router.get("/test", response_model=List[schemas.StadiumSchemas])
def read_stadiums_test(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    stadiums = crud_stadium.get_stadiums(db, skip=skip, limit=limit)
    return stadiums


@router.get("/", response_model=List[schemas.StadiumSchemas])
def read_stadiums(
    request: Request, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    stadiums = crud_stadium.get_stadiums(db, skip=skip, limit=limit)
    return templates.TemplateResponse(
        "stadiums.html",
        {
            "request": request,
            "stadiums": stadiums,
        },
    )


@router.get("/{stadium_id}", response_model=schemas.StadiumSchemas)
def read_stadium(stadium_id: int, db: Session = Depends(get_db)):
    db_stadium = crud_stadium.get_stadium(db, stadium_id=stadium_id)
    if db_stadium is None:
        raise HTTPException(status_code=404, detail="Stadium not found")
    return db_stadium


@router.put("/{stadium_id}", response_model=schemas.StadiumSchemas)
def update_stadium(
    stadium_id: int,
    stadium: schemas.StadiumUpdateSchemas,
    db: Session = Depends(get_db),
):
    db_stadium = crud_stadium.update_stadium(
        db=db, stadium_id=stadium_id, stadium=stadium
    )
    if db_stadium is None:
        raise HTTPException(status_code=404, detail="Stadium not found")
    return db_stadium


@router.delete("/{stadium_id}", response_model=schemas.StadiumSchemas)
def delete_stadium(stadium_id: int, db: Session = Depends(get_db)):
    db_stadium = crud_stadium.delete_stadium(db=db, stadium_id=stadium_id)
    if db_stadium is None:
        raise HTTPException(status_code=404, detail="Stadium not found")
    return db_stadium
