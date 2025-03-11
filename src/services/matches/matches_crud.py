""" DESCRIPTIONS:
sqlalchemy functions for CRUD operations
"""

from typing import Optional

from sqlalchemy import update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy.future import select


from models import Match
from validation import match as schemas


async def create_match(db: AsyncSession, match: schemas.MatchCreateSchemas):
    new_match = Match(**match.dict())
    db.add(new_match)
    await db.commit()
    await db.refresh(new_match)
    return new_match


def update_match(db: Session, match_id: int, match: schemas.MatchUpdateSchemas):

    db_match = db.query(Match).filter(Match.id == match_id).first()

    if db_match is None:
        return None
    for key, value in match.dict().items():
        setattr(db_match, key, value)
    db.commit()
    db.refresh(db_match)
    return db_match


async def update_match(db: AsyncSession, match_id: int, match: schemas.MatchUpdateSchemas) -> Optional[schemas.MatchSchemas]:

    async with db.begin():  # Запускає транзакцію
        query = (
            update(Match)
            .where(Match.id == match_id)
            .values(
                # Вставте всі поля, які потрібно оновити, з match
                team1=match.team1,
                team2=match.team2,
                date=match.date,
                # додайте інші поля
            )
            .returning(Match)
        )
        result = await db.execute(query)
        updated_match = result.scalars().first()
        if updated_match is None:
            return None
        return updated_match


async def delete_match(db: AsyncSession, match_id: int) -> Optional[schemas.MatchSchemas]:
    async with db.begin():  # Запускає транзакцію

        query = select(Match).where(Match.id == match_id)
        result = await db.execute(query)
        db_match = result.scalars().first()

        if db_match is None:
            return None

        query = delete(Match).where(Match.id == match_id)
        await db.execute(query)
        return db_match
