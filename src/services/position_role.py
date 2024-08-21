from sqlalchemy import desc
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


def get_persons_position_team(db: Session, person_id: int):
    # Виконання запиту для отримання даних
    result = (
        db.query(
            PositionRole.id,
            PositionRole.player_role_id,
            PlayerRole.full_name,
            Position.position,
            Team.id.label("team_id"),
            Team.name.label("team_name"),
            Team.city.label("team_city"),
        )
        .join(Position, Position.id == PositionRole.position_id)
        .join(TeamPerson, TeamPerson.id == PositionRole.team_person_id)
        .join(Team, Team.id == TeamPerson.team_id)
        .join(PlayerRole, PlayerRole.id == PositionRole.player_role_id)
        .filter(TeamPerson.person_id == person_id, PositionRole.active.is_(True))
        .all()
    )
    return result
