from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from models import Person, PositionRole, TeamPerson, Team, Position, PlayerRole


def get_persons_position(db: Session, person_id: int):
    # Виконання запиту для отримання даних
    result = (
        db.query(
            Team.id,
            Team.name,
            Team.city,
            PositionRole.position,
            PositionRole.player_role_id,
            PlayerRole.full_name,
        )
        .join(TeamPerson, PositionRole.team_person_id == TeamPerson.id)
        .join(Team, Team.id == TeamPerson.team_id)
        .join(PlayerRole, PlayerRole.id == PositionRole.player_role_id)
        .filter(TeamPerson.person_id == person_id, PositionRole.enddate.is_(None))
        .all()
    )
    return result


async def get_persons_position_team(db: AsyncSession, person_id: int):
    # Створення асинхронного запиту для отримання даних
    stmt = (
        select(
            PositionRole.id,
            PositionRole.player_role_id,
            PlayerRole.full_name,
            Position.position,
            Team.id.label("team_id"),
            Team.slug.label("team_slug"),
            Team.name.label("team_name"),
            Team.city.label("team_city"),
            Team.logo.label("team_logo"),
        )
        .join(Position, Position.id == PositionRole.position_id)
        .join(TeamPerson, TeamPerson.id == PositionRole.team_person_id)
        .join(Team, Team.id == TeamPerson.team_id)
        .join(PlayerRole, PlayerRole.id == PositionRole.player_role_id)
        .filter(TeamPerson.person_id == person_id, PositionRole.active.is_(True))
    )

    result = await db.execute(stmt)
    return result.all()
