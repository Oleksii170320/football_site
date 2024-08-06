from sqlalchemy.orm import Session
from models import organization as models
from validation import organization as schemas


def get_organization(db: Session, organization_id: int):
    return (
        db.query(models.Organization)
        .filter(models.Organization.id == organization_id)
        .first()
    )


def get_organizations(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Organization).offset(skip).limit(limit).all()


def create_organization(db: Session, organization: schemas.OrganizationCreateSchemas):
    db_organization = models.Organization(**organization.dict())
    db.add(db_organization)
    db.commit()
    db.refresh(db_organization)
    return db_organization


def update_organization(
    db: Session, organization_id: int, organization: schemas.OrganizationUpdateSchemas
):
    db_organization = (
        db.query(models.Organization)
        .filter(models.Organization.id == organization_id)
        .first()
    )
    if db_organization is None:
        return None
    for key, value in organization.dict().items():
        setattr(db_organization, key, value)
    db.commit()
    db.refresh(db_organization)
    return db_organization


def delete_organization(db: Session, organization_id: int):
    db_organization = (
        db.query(models.Organization)
        .filter(models.Organization.id == organization_id)
        .first()
    )
    if db_organization is None:
        return None
    db.delete(db_organization)
    db.commit()
    return db_organization
