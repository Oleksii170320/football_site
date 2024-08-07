from typing import TYPE_CHECKING
from sqlalchemy import String
from sqlalchemy.orm import relationship, mapped_column, Mapped
from sqlalchemy.ext.declarative import declared_attr
from slugify import slugify
from core.database import Base
from models.annonated import intpk

if TYPE_CHECKING:
    from models.match import Match


class Round(Base):
    __tablename__ = "rounds"

    id: Mapped[intpk]
    name: Mapped[str] = mapped_column(String(70), nullable=False)
    slug: Mapped[str] = mapped_column(String, nullable=True)

    # зв'язки з таблицями
    matches: Mapped["Match"] = relationship(
        back_populates="round",
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
