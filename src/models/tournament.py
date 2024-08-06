from typing import TYPE_CHECKING
from sqlalchemy import String, Text, Integer, ForeignKey, Column
from sqlalchemy.orm import relationship, mapped_column, Mapped
from slugify import slugify

from core.database import Base
from models.annonated import intpk

if TYPE_CHECKING:
    from models.organization import Organization
    from models.season import Season
    from models.news import News


class Tournament(Base):
    __tablename__ = "tournaments"
    __table_args__ = (
        # Index("region_index", 'name'),
    )

    id: Mapped[intpk]
    name: Mapped[str] = mapped_column(String(70), nullable=False)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    slug: Mapped[str] = mapped_column(String(256), nullable=False, unique=True)
    logo: Mapped[str | None] = mapped_column(String(256))
    description: Mapped[str] = mapped_column(
        Text, default="", server_default="", nullable=True
    )
    football_type: Mapped[str | None] = mapped_column(String(25))
    website: Mapped[str | None] = mapped_column(String)

    # зовнішні ключі
    organization_id: Mapped[int | None] = mapped_column(
        ForeignKey("organizations.id", onupdate="SET NULL", ondelete="SET NULL"),
    )

    # зв'язки з таблицями
    organization: Mapped["Organization"] = relationship(
        back_populates="tournaments",
    )
    seasons: Mapped[list["Season"]] = relationship(
        back_populates="tournament",
    )
    newstables: Mapped[list["News"]] = relationship(
        back_populates="tournament",
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if "slug" not in kwargs and "full_name" in kwargs:
            self.slug = self.generate_slug(kwargs["full_name"])

    def generate_slug(self, full_name: str) -> str:
        return slugify(full_name)
