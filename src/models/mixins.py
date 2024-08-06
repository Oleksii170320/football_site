from typing import TYPE_CHECKING
from sqlalchemy.orm import declared_attr, Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey


if TYPE_CHECKING:
    from models import Region


class RegionRelationMixin:
    _region_id_nullable: bool = False
    _region_id_unique: bool = False
    _region_back_populates: str | None = None

    @declared_attr
    def region_id(cls) -> Mapped[int]:
        return mapped_column(
            ForeignKey("regions.id"),
            unique=cls._region_id_unique,
            nullable=cls._region_id_nullable,
        )

    @declared_attr
    def region(cls) -> Mapped["Region"]:
        return relationship(
            "Region",
            back_populates=cls._region_back_populates,
        )
