from typing import TYPE_CHECKING
from enum import Enum
from sqlalchemy import Column, Enum as SQLAlchemyEnum, BigInteger, Boolean
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import relationship, mapped_column, Mapped

from core.database import Base
from models.annonated import intpk

if TYPE_CHECKING:
    from models import Team
    from models.stadium import Stadium
    from models.season import Season
    from models.group import Group


class MatchStatus(str, Enum):
    not_played = "Не зіграно"
    played = "Зіграно"
    technical_defeat = "Тех. поразка"
    postponed = "Перенесено"
    canceled = "Не відбудеться"


class Match(Base):
    __tablename__ = "matches"

    id: Mapped[intpk]
    # event: Mapped[str | None] = mapped_column()
    event = Column(BigInteger, nullable=True)
    season_id: Mapped[int | None] = mapped_column(
        ForeignKey("seasons.id", onupdate="SET NULL", ondelete="SET NULL"),
    )
    group_id: Mapped[int | None] = mapped_column(
        ForeignKey("groups.id", onupdate="SET NULL", ondelete="SET NULL"), nullable=True
    )
    round: Mapped[str | None] = mapped_column(String(20))
    stadium_id: Mapped[int | None] = mapped_column(
        ForeignKey("stadiums.id", onupdate="SET NULL", ondelete="SET NULL"),
    )
    team1_id: Mapped[int] = mapped_column(
        ForeignKey("teams.id", onupdate="SET NULL", ondelete="SET NULL"),
    )
    team1_goals: Mapped[int | None] = mapped_column(
        default="", server_default="", nullable=True
    )
    team2_goals: Mapped[int | None] = mapped_column(
        default="", server_default="", nullable=True
    )
    team2_id: Mapped[int] = mapped_column(
        ForeignKey("teams.id", onupdate="SET NULL", ondelete="SET NULL"),
    )
    status = Column(
        SQLAlchemyEnum(MatchStatus),
        default=MatchStatus.not_played,
        server_default=MatchStatus.not_played.value,
        nullable=False,
    )
    standing: Mapped[bool] = mapped_column(
        default=1, server_default="1", nullable=False
    )
    # зв'язки з таблицями
    stadium: Mapped["Stadium"] = relationship(
        "Stadium",
        back_populates="matches",
    )
    season: Mapped["Season"] = relationship(
        back_populates="matches",
    )
    group: Mapped["Group"] = relationship(
        back_populates="matches",
    )
    team_1: Mapped["Team"] = relationship(
        "Team",
        foreign_keys=[team1_id],
        back_populates="matches_1",
    )
    team_2: Mapped["Team"] = relationship(
        "Team",
        foreign_keys=[team2_id],
        back_populates="matches_2",
    )
