from typing import TYPE_CHECKING

from slugify import slugify
from sqlalchemy import (
    MetaData,
    String,
    Column,
    BigInteger,
)
from sqlalchemy.orm import relationship, mapped_column, Mapped, declared_attr

from core.database import Base
from models.annonated import intpk
from models.mixins import RegionRelationMixin

if TYPE_CHECKING:
    from models.team import Team


metadata = MetaData()


class Person(RegionRelationMixin, Base):
    __tablename__ = "persons"
    _region_id_nullable: bool = True
    # _region_id_unique: bool = False
    _region_back_populates = "teams"

    _region_id_nullable: bool = True
    _region_id_unique: bool = False
    _region_back_populates = "persons"

    id: Mapped[intpk]
    name: Mapped[str] = mapped_column(String(30), nullable=False)
    surname: Mapped[str] = mapped_column(String(30), nullable=True)
    lastname: Mapped[str] = mapped_column(String(40), nullable=False)
    birthday = Column(BigInteger, nullable=True)
    photo: Mapped[str | None] = mapped_column(String(256))
    slug: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)

    # зв'язки з таблицями
    team_president: Mapped[list["Team"]] = relationship(
        "Team",
        foreign_keys="[Team.president_id]",
        back_populates="president",
    )
    team_coach: Mapped[list["Team"]] = relationship(
        "Team",
        foreign_keys="[Team.coach_id]",
        back_populates="coach",
    )

    # many-to-many relationship to Team, bypassing the TeamPerson class
    teams_associations: Mapped[list["Team"]] = relationship(
        secondary="team_person_association",
        back_populates="persons_associations",
    )

    @declared_attr
    def __mapper_args__(cls):
        return {"confirm_deleted_rows": False}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if "slug" not in kwargs and "name" in kwargs:
            self.slug = self.generate_slug(
                kwargs["name"], kwargs["surname"], kwargs["lastname"]
            )

    def generate_slug(self, name: str, surname: str, lastname: str) -> str:
        return slugify(f"{name}-{surname}-{lastname}")
