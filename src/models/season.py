from typing import TYPE_CHECKING, Optional

from slugify import slugify
from sqlalchemy import Integer, BigInteger, String, ForeignKey
from sqlalchemy.orm import relationship, mapped_column, Mapped, declared_attr

from core.database import Base
from models.annonated import intpk

if TYPE_CHECKING:
    from models.tournament import Tournament
    from models.team import Team
    from models.match import Match
    from models.group import Group


class Season(Base):
    __tablename__ = "seasons"

    id: Mapped[intpk]
    name: Mapped[str] = mapped_column(String(70), nullable=False)
    start_date: Mapped[BigInteger | None] = mapped_column(BigInteger)
    end_date: Mapped[BigInteger | None] = mapped_column(BigInteger)
    year: Mapped[str | None] = mapped_column(String(20))
    standing: Mapped[bool] = mapped_column(
        default=1, server_default="1", nullable=False
    )
    slug: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)

    # зовнішні ключі
    tournament_id: Mapped[int] = mapped_column(
        ForeignKey("tournaments.id", ondelete="CASCADE"),
    )
    team_winner_id: Mapped[int | None] = mapped_column(
        ForeignKey("teams.id", onupdate="SET NULL", ondelete="SET NULL"), nullable=True
    )

    # зв'язки з таблицями
    tournament: Mapped["Tournament"] = relationship(
        back_populates="seasons",
    )
    team_winner: Mapped["Team"] = relationship(
        "Team", back_populates="seasons_won", foreign_keys=[team_winner_id]
    )
    matches: Mapped["Match"] = relationship(
        back_populates="season",
    )
    # groups: Mapped[Optional[list["Group"]]] = relationship(
    #     back_populates="season", lazy="selectin"
    # )

    # many-to-many relationship to Team, bypassing the TeamSeason class
    teams_associations: Mapped[list["Team"]] = relationship(
        secondary="team_seasons_association",
        back_populates="seasons_associations",
    )

    @declared_attr
    def __mapper_args__(cls):
        return {"confirm_deleted_rows": False}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if "slug" not in kwargs and "name" in kwargs:
            self.slug = self.generate_slug(kwargs["name"], kwargs["year"])

    def generate_slug(self, name: str, year: str) -> str:
        return slugify(f"{name}-{year}")
