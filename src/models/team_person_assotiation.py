from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base
from models.annonated import intpk

from models.position_role import PositionRole


class TeamPerson(Base):
    __tablename__ = "team_person_association"
    __table_args__ = (
        UniqueConstraint("team_id", "person_id", name="idx_unique_person_team"),
        # Index("organization_index", 'name'),
    )

    id: Mapped[intpk]
    team_id: Mapped[int] = mapped_column(
        ForeignKey("teams.id", onupdate="SET NULL", ondelete="SET NULL"),
    )
    person_id: Mapped[int] = mapped_column(
        ForeignKey("persons.id", onupdate="SET NULL", ondelete="SET NULL"),
    )

    # зв'язки з таблицями
    positions_role: Mapped[list["PositionRole"]] = relationship(
        back_populates="team_person",
    )
    match_properties: Mapped["MatchProperties"] = relationship(
        back_populates="player",
    )
