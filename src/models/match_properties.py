from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base
from models.annonated import intpk

if TYPE_CHECKING:
    from models.match import Match
    from models.match_event import MatchEvent
    from models.position_role import PositionRole


class MatchProperties(Base):
    __tablename__ = "match_properties"

    id: Mapped[intpk]
    protocol: Mapped[bool | None] = mapped_column(
        default=1, server_default="1", nullable=False
    )
    starting: Mapped[bool | None] = mapped_column(
        default=0, server_default="0", nullable=False
    )
    start_min: Mapped[int | None] = mapped_column(
        default=0, server_default="0", nullable=False
    )
    end_min: Mapped[int | None] = mapped_column(
        default=0, server_default="0", nullable=False
    )

    # зовнішні ключі
    match_id: Mapped[int] = mapped_column(
        ForeignKey("matches.id", onupdate="SET NULL", ondelete="SET NULL"),
    )
    player_id: Mapped[int] = mapped_column(
        ForeignKey("positions_role.id", onupdate="SET NULL", ondelete="SET NULL"),
        nullable=False,
    )

    # зв'язки з таблицями
    matches: Mapped["Match"] = relationship(
        back_populates="match_properties",
    )
    player: Mapped["PositionRole"] = relationship(
        back_populates="match_properties",
    )
    matches_event: Mapped[list["MatchEvent"]] = relationship(
        "MatchEvent",
        foreign_keys="[MatchEvent.player_match_id]",
        back_populates="player_match",
    )
    matches_replacement: Mapped[list["MatchEvent"]] = relationship(
        "MatchEvent",
        foreign_keys="[MatchEvent.player_replacement_id]",
        back_populates="player_replacement",
    )
