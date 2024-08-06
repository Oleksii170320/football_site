from typing import TYPE_CHECKING

from slugify import slugify
from sqlalchemy import (
    MetaData,
    String,
    Text,
)
from sqlalchemy.orm import relationship, mapped_column, Mapped, declared_attr

from core.database import Base
from models.annonated import intpk

if TYPE_CHECKING:
    from models.tournament import Organization


metadata = MetaData()


class Association(Base):
    __tablename__ = "associations"

    id: Mapped[intpk]
    name: Mapped[str] = mapped_column(String(10), nullable=False)
    slug: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)
    full_name: Mapped[str] = mapped_column(String(256), nullable=False)
    description: Mapped[str | None] = mapped_column(
        Text, default="", server_default="", nullable=True
    )
    logo: Mapped[str | None] = mapped_column(String(256))
    website: Mapped[str | None] = mapped_column(String)

    # зв'язки з таблицями
    organizations: Mapped[list["Organization"]] = relationship(
        back_populates="association",
    )

    @declared_attr
    def __mapper_args__(cls):
        return {"confirm_deleted_rows": False}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if "slug" not in kwargs and "name" in kwargs:
            self.slug = self.generate_slug(kwargs["name"])

    def generate_slug(self, name: str) -> str:
        return slugify(f"{name}")
