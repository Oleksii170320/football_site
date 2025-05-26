# from typing import TYPE_CHECKING
# from slugify import slugify
# from sqlalchemy import   String, Text, ForeignKey
# from sqlalchemy.orm import relationship, mapped_column, Mapped, declared_attr
#
# from core.database import Base
# from models.annonated import intpk
# from models.mixins import RegionRelationMixin
#
#
# if TYPE_CHECKING:
#     from models.season import Season
#     from models.team import Team
#
#
# class CeasonWinners(RegionRelationMixin, Base):
#     __tablename__ = "season_winners"
#
#     id: Mapped[intpk]
#     prize_place: int
#     description: Mapped[str] = mapped_column(Text, default="", server_default="", nullable=True)
#
# # зовнішні ключі
#     team_id: Mapped[int | None] = mapped_column(ForeignKey("teams.id", onupdate="SET NULL", ondelete="SET NULL"), nullable=True)
#     season_id: Mapped[int | None] = mapped_column(ForeignKey("seasons.id", onupdate="SET NULL", ondelete="SET NULL"), nullable=True)
#
# # зв'язки з таблицями
#     season: Mapped["Season"] = relationship(back_populates="winner_season", )
#     team: Mapped["Team"] = relationship(back_populates="winner_team", )
#
#
#
#
#
