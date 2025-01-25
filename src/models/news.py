from typing import TYPE_CHECKING
from sqlalchemy import BigInteger, ForeignKey, Column
from sqlalchemy.orm import relationship, mapped_column, Mapped

from core.database import Base
from models.annonated import intpk

if TYPE_CHECKING:
    from models.region import Region


class News(Base):
    __tablename__ = "news"

    id: Mapped[intpk]
    event = Column(BigInteger, nullable=True)
    topic: Mapped[str]
    brief: Mapped[str | None]
    description: Mapped[str | None]
    photo: Mapped[str | None]
    region_id: Mapped[int] = mapped_column(
        ForeignKey("regions.id", onupdate="SET NULL", ondelete="SET NULL"),
    )
    # region_id: Mapped[int] = mapped_column(
    #     ForeignKey("tournaments.id", onupdate="SET NULL", ondelete="SET NULL"),
    # )

    # зв'язки з таблицями
    region: Mapped["Region"] = relationship(
        back_populates="newstables",
    )
    # tournament: Mapped["Tournament"] = relationship(
    #     back_populates="newstables",
    # )
