from sqlalchemy.orm import Session

from models import Person
from models.position import Position
from validation import position as schemas


def get_positions(db: Session):
    position_list = db.query(Position).all()
    return position_list


def get_position(db: Session, position_id: int):
    return db.query(Position).filter(Position.id == position_id).first()


def create_person(db: Session, position: schemas.PositionSchemas):
    db_position = Person(**position.dict())
    db.add(db_position)
    db.commit()
    db.refresh(db_position)
    return db_position


def update_person(
    db: Session, position_id: int, position: schemas.PositionUpdateSchemas
):
    db_position = db.query(Position).filter(Position.id == position_id).first()
    if db_position is None:
        return None
    for key, value in position.dict().items():
        setattr(db_position, key, value)
    db.commit()
    db.refresh(db_position)
    return db_position


def delete_person(db: Session, position_id: int):
    db_position = db.query(Position).filter(Position.id == position_id).first()
    if db_position is None:
        return None
    db.delete(db_position)
    db.commit()
    return db_position
