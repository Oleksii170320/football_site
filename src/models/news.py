from typing import TYPE_CHECKING
from sqlalchemy import BigInteger, ForeignKey, Column
from sqlalchemy.orm import relationship, mapped_column, Mapped

from core.database import Base
from models.annonated import intpk

if TYPE_CHECKING:
    from models.tournament import Tournament


class News(Base):
    __tablename__ = "news"

    id: Mapped[intpk]
    event = Column(BigInteger, nullable=True)
    topic: Mapped[str]
    brief: Mapped[str | None]
    description: Mapped[str | None]
    photo: Mapped[str | None]
    # created_at = Mapped[int] = mapped_column(BigInteger, default=lambda: int(time.time()))
    category_id: Mapped[int] = mapped_column(
        ForeignKey("tournaments.id", onupdate="SET NULL", ondelete="SET NULL"),
    )

    # зв'язки з таблицями
    tournament: Mapped["Tournament"] = relationship(
        back_populates="newstables",
    )
