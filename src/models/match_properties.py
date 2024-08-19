from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, UniqueConstraint, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base
from models.annonated import intpk

from models.match import Match
from models.team_person_assotiation import TeamPerson
from models.position_role import PositionRole
from models.person import Person


class MatchProperties(Base):
    __tablename__ = "match_properties"

    id: Mapped[intpk]
    protocol: Mapped[bool | None] = mapped_column(
        default=1, server_default="1", nullable=False
    )
    starting: Mapped[bool | None] = mapped_column(
        default=0, server_default="0", nullable=False
    )
    replacement: Mapped[bool] = mapped_column(
        default=0, server_default="0", nullable=False
    )
    minutes: Mapped[int | None] = mapped_column(
        default=0, server_default="0", nullable=False
    )
    goals: Mapped[int | None] = mapped_column(
        default=0, server_default="0", nullable=False
    )
    goals_penalty: Mapped[int | None] = mapped_column(
        default=0, server_default="0", nullable=False
    )
    own_goal: Mapped[int | None] = mapped_column(
        default=0, server_default="0", nullable=False
    )
    yellow_card: Mapped[bool] = mapped_column(
        default=0, server_default="0", nullable=False
    )
    second_yellow_card: Mapped[bool] = mapped_column(
        default=0, server_default="0", nullable=False
    )
    red_card: Mapped[bool] = mapped_column(
        default=0, server_default="0", nullable=False
    )

    # зовнішні ключі
    match_id: Mapped[int] = mapped_column(
        ForeignKey("matches.id", onupdate="SET NULL", ondelete="SET NULL"),
    )
    # player_id: Mapped[int] = mapped_column(
    #     ForeignKey("positions_role.id", onupdate="SET NULL", ondelete="SET NULL"),
    #     nullable=False,
    # )
    # person_id: Mapped[int] = mapped_column(
    #     ForeignKey("persons.id", onupdate="CASCADE", ondelete="CASCADE"),
    #     nullable=False,
    # )
    player_id: Mapped[int] = mapped_column(
        ForeignKey(
            "team_person_association.id", onupdate="SET NULL", ondelete="SET NULL"
        ),
        nullable=False,
    )

    # зв'язки з таблицями
    matches: Mapped["Match"] = relationship(
        back_populates="match_properties",
    )
    # player: Mapped["PositionRole"] = relationship(
    #     back_populates="match_properties",
    # )
    # person: Mapped["Person"] = relationship(
    #     back_populates="match_properties",
    # )
    player: Mapped["TeamPerson"] = relationship(
        back_populates="match_properties",
    )
