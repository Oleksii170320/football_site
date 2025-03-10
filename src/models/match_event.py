from typing import TYPE_CHECKING
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import relationship, mapped_column, Mapped

from core.database import Base
from models.annonated import intpk

if TYPE_CHECKING:
    from models.ref_event import RefEvent
    from models.match_properties import MatchProperties


class MatchEvent(Base):
    __tablename__ = "matches_event"

    id: Mapped[intpk]
    player_match_id: Mapped[int] = mapped_column(ForeignKey("match_properties.id", onupdate="SET NULL", ondelete="SET NULL"),)
    event_id: Mapped[int] = mapped_column(ForeignKey("ref_event.id", onupdate="SET NULL", ondelete="SET NULL"),)
    minute: Mapped[str] = mapped_column(String(10), nullable=False)
    player_replacement_id: Mapped[int | None] = mapped_column(ForeignKey("match_properties.id", onupdate="SET NULL", ondelete="SET NULL"),)

    # зв'язки з таблицями
    event: Mapped["RefEvent"] = relationship(
        back_populates="matches_event",
    )
    player_match: Mapped["MatchProperties"] = relationship(
        "MatchProperties",
        foreign_keys=[player_match_id],
        back_populates="matches_event",
    )
    player_replacement: Mapped["MatchProperties"] = relationship(
        "MatchProperties",
        foreign_keys=[player_replacement_id],
        back_populates="matches_replacement",
    )
