from sqlalchemy.orm import Session
from models import stadium as models
from validation import stadium as schemas


def get_stadium(db: Session, stadium_id: int):
    return db.query(models.Stadium).filter(models.Stadium.id == stadium_id).first()


def get_stadiums(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Stadium).offset(skip).limit(limit).all()


def create_stadium(db: Session, stadium: schemas.StadiumCreateSchemas):
    db_stadium = models.Stadium(**stadium.dict())
    db.add(db_stadium)
    db.commit()
    db.refresh(db_stadium)
    return db_stadium


def update_stadium(db: Session, stadium_id: int, stadium: schemas.StadiumUpdateSchemas):
    db_stadium = (
        db.query(models.Stadium).filter(models.Stadium.id == stadium_id).first()
    )
    if db_stadium is None:
        return None
    for key, value in stadium.dict().items():
        setattr(db_stadium, key, value)
    db.commit()
    db.refresh(db_stadium)
    return db_stadium


def delete_stadium(db: Session, stadium_id: int):
    db_stadium = (
        db.query(models.Stadium).filter(models.Stadium.id == stadium_id).first()
    )
    if db_stadium is None:
        return None
    db.delete(db_stadium)
    db.commit()
    return db_stadium
