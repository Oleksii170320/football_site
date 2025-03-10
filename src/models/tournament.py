from enum import Enum
from typing import TYPE_CHECKING
from sqlalchemy import String, Text, ForeignKey, Enum as SQLAlchemyEnum, Column
from sqlalchemy.orm import relationship, mapped_column, Mapped
from slugify import slugify

from core.database import Base
from models.annonated import intpk

if TYPE_CHECKING:
    from models.organization import Organization
    from models.season import Season
    from models.football_type import FootbalType


class FootballType(str, Enum):
    football = "Футбол"
    futsal = "Футзал"
    mini_football = "Міні-футбол"
    beach_soccer = "Пляжний футбол"
    street_football = "Вуличний футбол"


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
    description: Mapped[str] = mapped_column(Text, default="", server_default="", nullable=True)
    football_type = Column(
        SQLAlchemyEnum(FootballType),
        default=FootballType.football,
        server_default=FootballType.football.value,
        nullable=False,
    )
    website: Mapped[str | None] = mapped_column(String)
    page_facebook: Mapped[str | None] = mapped_column(String)
    page_youtube: Mapped[str | None] = mapped_column(String)
    page_telegram: Mapped[str | None] = mapped_column(String)
    page_instagram: Mapped[str | None] = mapped_column(String)
    level_int: Mapped[int | None]
    level: Mapped[str | None]
    level_up: Mapped[str | None]
    level_down: Mapped[str | None]
    create_year: Mapped[str | None]

    # зовнішні ключі
    organization_id: Mapped[int | None] = mapped_column(
        ForeignKey("organizations.id", onupdate="SET NULL", ondelete="SET NULL"),
    )
    football_type_id: Mapped[int] = mapped_column(
        ForeignKey("football_types.id", onupdate="SET NULL", ondelete="SET NULL"),
    )

    # зв'язки з таблицями
    organization: Mapped["Organization"] = relationship(
        back_populates="tournaments",
    )
    seasons: Mapped[list["Season"]] = relationship(
        back_populates="tournament",
    )
    football_types: Mapped["FootbalType"] = relationship(
        back_populates="tournaments",
    )
    # newstables: Mapped[list["News"]] = relationship(
    #     back_populates="tournament",
    # )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if "slug" not in kwargs and "full_name" in kwargs:
            self.slug = self.generate_slug(kwargs["full_name"])

    def generate_slug(self, full_name: str) -> str:
        return slugify(full_name)
