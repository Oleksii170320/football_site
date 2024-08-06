from typing import TYPE_CHECKING
from enum import Enum
from sqlalchemy import ForeignKey, String, Integer, Column, Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship, Mapped, mapped_column

from core.database import Base
from models.annonated import intpk
from models.mixins import RegionRelationMixin

if TYPE_CHECKING:
    from models.team import Team
    from models.match import Match


class TypeCoverage(str, Enum):
    natural = "Натуральне"
    artificial = "Штучне"
    rubber = "Резинове"
    parquet = "Паркет"
    not_specified = "не вказано"


class Stadium(RegionRelationMixin, Base):
    __tablename__ = "stadiums"
    __table_args__ = (
        # Index("region_index", 'name'),
        # CheckConstraint("compensation > 0", name='check_compensation_positive'),
    )
    _region_id_nullable: bool = True
    # _region_id_unique: bool = False
    _region_back_populates = "stadiums"

    id: Mapped[intpk]
    name: Mapped[str] = mapped_column(String(70), nullable=False)
    city: Mapped[str] = mapped_column(String(70), nullable=True)
    address: Mapped[str | None] = mapped_column(
        String(200),
    )
    photo: Mapped[str | None] = mapped_column(
        String(256),
    )
    capacity: Mapped[str | None] = mapped_column(String(30), default="-", nullable=True)
    dimensions: Mapped[str | None] = mapped_column(
        String(20),
    )
    type_coverage = Column(
        SQLAlchemyEnum(TypeCoverage),
        default=TypeCoverage.not_specified,
        server_default=TypeCoverage.not_specified.value,
        nullable=True,
    )

    # зв'язки з таблицями
    teams: Mapped[list["Team"]] = relationship(
        back_populates="stadium",
    )
    matches: Mapped[list["Match"]] = relationship(
        "Match",
        back_populates="stadium",
    )

    # зовнішні ключі
    # region_id: Mapped[int | None] = mapped_column(
    #     Integer,
    #     ForeignKey("regions.id", onupdate="SET NULL", ondelete="SET NULL"),
    #     nullable=True,
    # )

    # зв'язки з таблицями
    # region: Mapped["Region"] = relationship(
    #     back_populates="stadiums",
    # )
