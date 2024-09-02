from sqlalchemy.orm import Session

from models import Region
from models.organization import Organization
from validation import organization as schemas


def get_organization(db: Session, organization_id: int):
    return db.query(Organization).filter(Organization.id == organization_id).first()


def get_region_organization(db: Session, region_slug: str):
    return (
        db.query(
            Region.id.label("region_id"),
            Organization.id.label("organization_id"),
            Organization.slug,
            Organization.logo,
            Organization.name,
            Organization.full_name,
            Organization.description,
            Organization.website,
            Organization.tournament_level,
        )
        .join(Organization, Organization.region_id == Region.id)
        .filter(Region.slug == region_slug)
        .all()
    )


def get_organizations(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Organization).offset(skip).limit(limit).all()


def create_organization(db: Session, organization: schemas.OrganizationCreateSchemas):
    db_organization = Organization(**organization.dict())
    db.add(db_organization)
    db.commit()
    db.refresh(db_organization)
    return db_organization


def update_organization(
    db: Session, organization_id: int, organization: schemas.OrganizationUpdateSchemas
):
    db_organization = (
        db.query(Organization).filter(Organization.id == organization_id).first()
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
        db.query(Organization).filter(Organization.id == organization_id).first()
    )
    if db_organization is None:
        return None
    db.delete(db_organization)
    db.commit()
    return db_organization
