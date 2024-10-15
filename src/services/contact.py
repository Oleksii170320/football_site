from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from models import (
    Contact,
    Region,
)


def get_contacts(db: Session):
    return db.query(Contact).all()


async def get_contact(db: AsyncSession, region_slug: str):
    """Запит контактних даних футбольної органызації області"""

    result = await db.execute(
        select(
            Contact.telephone,
            Contact.email,
            Contact.address,
        )
        .join(Region, Region.id == Contact.region_id)
        .filter(Region.slug == region_slug)
    )
    return result.first()
