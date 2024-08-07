from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import String, ForeignKey, Enum as SQLAlchemyEnum, Column
from sqlalchemy.orm import relationship, mapped_column, Mapped
from sqlalchemy.ext.declarative import declared_attr
from slugify import slugify

from core.database import Base
from models.annonated import intpk


if TYPE_CHECKING:
    from models.season import Season
    from models.match import Match


class Group(Base):
    __tablename__ = "groups"

    id: Mapped[intpk]
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    slug: Mapped[str] = mapped_column(String, nullable=True)

    # зовнішні ключі
    season_id: Mapped[int | None] = mapped_column(
        ForeignKey("seasons.id", onupdate="SET NULL", ondelete="SET NULL"),
    )

    # зв'язки з таблицями
    season: Mapped["Season"] = relationship(
        back_populates="groups",
    )
    matches: Mapped["Match"] = relationship(
        back_populates="group",
    )

    @declared_attr
    def __mapper_args__(cls):
        return {"confirm_deleted_rows": False}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if "slug" not in kwargs and "name" in kwargs:
            self.slug = self.generate_slug(self.name)

    def generate_slug(self, name: str) -> str:
        return slugify(name)
