from typing import TYPE_CHECKING
from enum import Enum
from sqlalchemy import Column, Enum as SQLAlchemyEnum, BigInteger
from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import relationship, mapped_column, Mapped

from core.database import Base
from models.annonated import intpk

if TYPE_CHECKING:
    from models import Team
    from models.stadium import Stadium
    from models.season import Season
    from models.group import Group
    from models.stage import Stage
    from models.round import Round
    from models.match_properties import MatchProperties


class MatchStatus(str, Enum):
    not_played = "Не зіграно"
    played = "Зіграно"
    technical_defeat = "Тех. поразка"
    postponed = "Перенесено"
    not_finished = "Не дограно"
    canceled = "Не відбудеться"


class Match(Base):
    __tablename__ = "matches"

    id: Mapped[intpk]
    event: Mapped[int] = mapped_column(BigInteger, nullable=False, default=4102437600)
    season_id: Mapped[int | None] = mapped_column(
        ForeignKey("seasons.id", onupdate="SET NULL", ondelete="SET NULL"),
    )
    group_id: Mapped[int | None] = mapped_column(
        ForeignKey("groups.id", onupdate="SET NULL", ondelete="SET NULL"), nullable=True
    )
    round_id: Mapped[int | None] = mapped_column(
        ForeignKey("rounds.id", onupdate="SET NULL", ondelete="SET NULL"), nullable=True
    )
    stadium_id: Mapped[int | None] = mapped_column(
        ForeignKey("stadiums.id", onupdate="SET NULL", ondelete="SET NULL"),
    )
    stage_id: Mapped[int | None] = mapped_column(
        ForeignKey("stages.id", onupdate="SET NULL", ondelete="SET NULL"),
    )
    team1_id: Mapped[int] = mapped_column(ForeignKey("teams.id", onupdate="SET NULL", ondelete="SET NULL"),)
    team1_goals: Mapped[int | None] = mapped_column(default="", server_default="", nullable=True)
    team2_goals: Mapped[int | None] = mapped_column(default="", server_default="", nullable=True)
    team2_id: Mapped[int] = mapped_column(ForeignKey("teams.id", onupdate="SET NULL", ondelete="SET NULL"),)
    extra_time: Mapped[bool] = mapped_column(default=0, server_default="0", nullable=False)
    team1_penalty: Mapped[int | None] = mapped_column(nullable=True )  # Після матчеві перальті - голи оманди 1
    team2_penalty: Mapped[int | None] = mapped_column(nullable=True)  # Після матчеві перальті - голи оманди 2
    status = Column(
        SQLAlchemyEnum(MatchStatus),
        default=MatchStatus.not_played,
        server_default=MatchStatus.not_played.value,
        nullable=False,
    )
    standing: Mapped[bool] = mapped_column(default=1, server_default="1", nullable=False)
    match_info: Mapped[str] = mapped_column(Text, default="", server_default="", nullable=True)
    match_video: Mapped[str] = mapped_column(Text, default="", server_default="", nullable=True)

    # зв'язки з таблицями
    stadium: Mapped["Stadium"] = relationship("Stadium", back_populates="matches",)
    season: Mapped["Season"] = relationship(back_populates="matches",)
    group: Mapped["Group"] = relationship(back_populates="matches",)
    round: Mapped["Round"] = relationship(back_populates="matches",)
    stage: Mapped["Stage"] = relationship(back_populates="matches",)
    team_1: Mapped["Team"] = relationship("Team", foreign_keys=[team1_id], back_populates="matches_1",)
    match_properties: Mapped[list["MatchProperties"]] = relationship(back_populates="matches",)
    # many-to-many relationship to Team, bypassing the MatchTeam class
    team_2: Mapped["Team"] = relationship(foreign_keys=[team2_id], back_populates="matches_2",)
