from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from core.database import Base
from models.annonated import intpk


class TeamSeason(Base):
    __tablename__ = "team_seasons_association"
    __table_args__ = (
        UniqueConstraint("team_id", "season_id", name="idx_unique_season_team"),
        # Index("organization_index", 'name'),
    )

    id: Mapped[intpk]
    comment: Mapped[str | None] = mapped_column()
    # зовнішні ключі
    team_id: Mapped[int] = mapped_column(
        ForeignKey("teams.id", onupdate="SET NULL", ondelete="SET NULL"),
    )
    season_id: Mapped[int] = mapped_column(
        ForeignKey("seasons.id", onupdate="SET NULL", ondelete="SET NULL"),
    )
