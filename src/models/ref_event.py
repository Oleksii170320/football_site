from typing import TYPE_CHECKING
from sqlalchemy import String
from sqlalchemy.orm import relationship, mapped_column, Mapped

from core.database import Base
from models.annonated import intpk

if TYPE_CHECKING:
    from models.match_event import MatchEvent


class RefEvent(Base):
    __tablename__ = "ref_event"

    id: Mapped[intpk]
    name: Mapped[str] = mapped_column(String(35), nullable=False)
    slug: Mapped[str] = mapped_column(String(40), nullable=False)
    image: Mapped[str] = mapped_column(String(256), nullable=False)

    # зв'язки з таблицями
    matches_event: Mapped[list["MatchEvent"]] = relationship(
        back_populates="event",
    )
