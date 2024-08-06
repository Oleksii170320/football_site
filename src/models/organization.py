from typing import TYPE_CHECKING

from slugify import slugify
from sqlalchemy import (
    MetaData,
    String,
    ForeignKey,
    Text,
    Column,
    Enum as SQLAlchemyEnum,
)
from sqlalchemy.orm import relationship, mapped_column, Mapped, declared_attr
from enum import Enum

from core.database import Base
from models.annonated import intpk
from models.mixins import RegionRelationMixin

if TYPE_CHECKING:
    from models.association import Association
    from models.tournament import Tournament


metadata = MetaData()


class TournamentLevel(str, Enum):
    repablic = "республ."
    region = "обласні"
    district = "районні"
    urban = "міські"
    not_specified = "не вказано"


class Organization(RegionRelationMixin, Base):
    __tablename__ = "organizations"

    _region_id_nullable: bool = True
    _region_id_unique: bool = False
    _region_back_populates = "organizations"

    id: Mapped[intpk]
    name: Mapped[str] = mapped_column(String(10), nullable=False)

    slug: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)
    full_name: Mapped[str] = mapped_column(String(256), nullable=False)
    description: Mapped[str | None] = mapped_column(
        Text, default="", server_default="", nullable=True
    )
    logo: Mapped[str | None] = mapped_column(String(256))
    website: Mapped[str | None] = mapped_column(String)
    tournament_level = Column(
        SQLAlchemyEnum(TournamentLevel),
        default=TournamentLevel.not_specified,
        server_default=TournamentLevel.not_specified.value,
        nullable=True,
    )

    # зовнішні ключі
    association_id: Mapped[int | None] = mapped_column(
        ForeignKey("associations.id", onupdate="SET NULL", ondelete="SET NULL"),
    )

    # зв'язки з таблицями
    tournaments: Mapped[list["Tournament"]] = relationship(
        back_populates="organization",
    )
    association: Mapped["Association"] = relationship(
        back_populates="organizations",
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
