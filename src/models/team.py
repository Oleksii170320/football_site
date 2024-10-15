from typing import TYPE_CHECKING
from slugify import slugify
from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship, mapped_column, Mapped, declared_attr

from core.database import Base
from models.annonated import intpk
from models.mixins import RegionRelationMixin


if TYPE_CHECKING:
    from models.stadium import Stadium
    from models.season import Season
    from models.match import Match
    from models.person import Person


class Team(RegionRelationMixin, Base):
    __tablename__ = "teams"
    _region_id_nullable: bool = True
    # _region_id_unique: bool = False
    _region_back_populates = "teams"

    id: Mapped[intpk]
    name: Mapped[str] = mapped_column(String(70), nullable=False)
    slug: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)
    full_name: Mapped[str | None] = mapped_column(String(120))
    city: Mapped[str | None] = mapped_column(String(50))
    foundation_year: Mapped[str | None] = mapped_column(String(20))
    logo: Mapped[str | None] = mapped_column(String(512))
    description: Mapped[str] = mapped_column(
        Text, default="", server_default="", nullable=True
    )
    clubs_site: Mapped[str] = mapped_column(
        Text, default="", server_default="", nullable=True
    )

    # зовнішні ключі
    stadium_id: Mapped[int | None] = mapped_column(
        ForeignKey("stadiums.id", onupdate="SET NULL", ondelete="SET NULL"),
    )
    president_id: Mapped[int | None] = mapped_column(
        ForeignKey("persons.id", onupdate="SET NULL", ondelete="SET NULL"),
    )
    coach_id: Mapped[int | None] = mapped_column(
        ForeignKey("persons.id", onupdate="SET NULL", ondelete="SET NULL"),
    )

    # зв'язки з таблицями
    stadium: Mapped["Stadium"] = relationship(
        back_populates="teams",
    )
    president: Mapped["Person"] = relationship(
        "Person",
        foreign_keys=[president_id],
        back_populates="team_president",
    )
    coach: Mapped["Person"] = relationship(
        "Person",
        foreign_keys=[coach_id],
        back_populates="team_coach",
    )
    matches_1: Mapped[list["Match"]] = relationship(
        "Match",
        foreign_keys="[Match.team1_id]",
        back_populates="team_1",
    )
    matches_2: Mapped[list["Match"]] = relationship(
        "Match",
        foreign_keys="[Match.team2_id]",
        back_populates="team_2",
    )
    seasons_won: Mapped[list["Season"]] = relationship(
        "Season", back_populates="team_winner", foreign_keys="[Season.team_winner_id]"
    )

    # many-to-many relationship to Season, bypassing the `TeamSeason`class
    seasons_associations: Mapped[list["Season"]] = relationship(
        secondary="team_seasons_association",
        back_populates="teams_associations",
    )
    # many-to-many relationship to Person, bypassing the `TeamPerson` class
    persons_associations: Mapped[list["Person"]] = relationship(
        secondary="team_person_association",
        back_populates="teams_associations",
    )

    @declared_attr
    def __mapper_args__(cls):
        return {"confirm_deleted_rows": False}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if "slug" not in kwargs and "name" in kwargs and "city" in kwargs:
            self.slug = self.generate_slug(kwargs["name"], kwargs["city"])
        elif "slug" not in kwargs and "name" in kwargs:
            self.slug = self.generate_slug(kwargs["name"])

    def generate_slug(self, name: str, city: str = "") -> str:
        if city:
            return slugify(f"{name}-{city}")
        return slugify(name)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not kwargs.get("slug") and kwargs.get("name"):
            if kwargs.get("city"):
                self.slug = self.generate_slug(kwargs["name"], kwargs["city"])
            else:
                self.slug = self.generate_slug(kwargs["name"])
