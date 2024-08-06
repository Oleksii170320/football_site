from sqlalchemy.orm import Session
from models.association import Association
from validation import association as schemas


def get_association(db: Session, association_id: int):
    return db.query(Association).filter(Association.id == association_id).first()


def get_associations(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Association).offset(skip).limit(limit).all()


def create_association(db: Session, association: schemas.AssociationCreateSchemas):
    db_association = Association(**association.dict())
    db.add(db_association)
    db.commit()
    db.refresh(db_association)
    return db_association


def update_association(
    db: Session, association_id: int, association: schemas.AssociationUpdateSchemas
):
    db_association = (
        db.query(Association).filter(Association.id == association_id).first()
    )
    if db_association is None:
        return None
    for key, value in association.dict().items():
        setattr(db_association, key, value)
    db.commit()
    db.refresh(db_association)
    return db_association


def delete_association(db: Session, association_id: int):
    db_association = (
        db.query(Association).filter(Association.id == association_id).first()
    )
    if db_association is None:
        return None
    db.delete(db_association)
    db.commit()
    return db_association
