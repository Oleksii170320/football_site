from typing import TYPE_CHECKING
from sqlalchemy import String
from sqlalchemy.orm import relationship, mapped_column, Mapped
from sqlalchemy.ext.declarative import declared_attr

from core.database import Base
from models.annonated import intpk
from slugify import slugify

if TYPE_CHECKING:
    from models.position_role import PositionRole


class Position(Base):
    __tablename__ = "positions"

    id: Mapped[intpk]
    position: Mapped[str] = mapped_column(String(40), nullable=False)
    slug: Mapped[str] = mapped_column(String, nullable=False, unique=True)

    # зв'язки з таблицями
    positions_role: Mapped["PositionRole"] = relationship(
        back_populates="position",
    )

    @declared_attr
    def __mapper_args__(cls):
        return {"confirm_deleted_rows": False}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if "slug" not in kwargs and "name" in kwargs:
            self.slug = self.generate_slug(self.position)

    def generate_slug(self, position: str) -> str:
        return slugify(position)
