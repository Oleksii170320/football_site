from typing import TYPE_CHECKING
from sqlalchemy import String,  UniqueConstraint
from sqlalchemy.orm import relationship, mapped_column, Mapped
from sqlalchemy.ext.declarative import declared_attr

from core.database import Base
from models.annonated import intpk
from slugify import slugify

if TYPE_CHECKING:
    from models.organization import Organization
    from models.team import Team
    from models.stadium import Stadium
    from models.person import Person
    from models.news import News

    from models.contacts import Contact


class Region(Base):
    __tablename__ = "regions"
    __table_args__ = (UniqueConstraint("slug", name="uq_region_slug"),)

    id: Mapped[intpk]
    name: Mapped[str] = mapped_column(String(30), nullable=False)
    emblem: Mapped[str | None] = mapped_column(String(256))
    slug: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)

    # зв'язки з таблицями
    organizations: Mapped[list["Organization"]] = relationship(
        back_populates="region",
        cascade="all, delete-orphan",
    )
    teams: Mapped[list["Team"]] = relationship(
        back_populates="region",
    )
    stadiums: Mapped[list["Stadium"]] = relationship(
        back_populates="region",
    )
    persons: Mapped[list["Person"]] = relationship(
        back_populates="region",
    )
    contact: Mapped[list["Contact"]] = relationship(
        back_populates="region",
    )
    newstables: Mapped[list["News"]] = relationship(
        back_populates="region",
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
