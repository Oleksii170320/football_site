from sqlalchemy.orm import Session

from models import (
    Contact,
    Region,
)


def get_contacts(db: Session):
    return db.query(Contact).all()


def get_contact(db: Session, region_slug: str):
    """Запит контактних даних футбольної органызації області"""

    result = (
        db.query(
            Contact.telephone,
            Contact.email,
            Contact.address,
        )
        .join(Region, Region.id == Contact.region_id)
        .filter(Region.slug == region_slug)
        .first()
    )
    return result
