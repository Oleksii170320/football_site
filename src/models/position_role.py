from typing import TYPE_CHECKING

from datetime import datetime
from enum import Enum
from sqlalchemy import (
    MetaData,
    Column,
    Enum as SQLAlchemyEnum,
    BigInteger,
    ForeignKey,
    Integer,
    CheckConstraint,
    Boolean,
    event,
)
from sqlalchemy.orm import relationship, mapped_column, Mapped
from core.database import Base
from models.annonated import intpk


if TYPE_CHECKING:
    from models.match_properties import MatchProperties


metadata = MetaData()


class TypeRole(str, Enum):
    goalkeeper = "Воротар"
    back = "Захисник"
    half_back = "Півзахисник"
    forward = "Нападник"
    universal = "Універсал"
    not_specified = "-"


class StrongLeg(str, Enum):
    only_rights = "Тільки права"
    right = "Зправа"
    only_left = "Тільки ліва"
    left = "Зліва"
    both = "Обидві"
    not_specified = "-"


class PositionRole(Base):
    __tablename__ = "positions_role"
    __table_args__ = (
        CheckConstraint(
            "player_number >= 0 AND player_number <= 99",
            name="check_player_number_range",
        ),
    )

    id: Mapped[intpk]
    player_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    startdate = Column(BigInteger, nullable=True)
    enddate = Column(BigInteger, nullable=True)
    active: Mapped[bool] = mapped_column(default=1, server_default="1", nullable=False)
    strong_leg = Column(
        SQLAlchemyEnum(StrongLeg),
        default=StrongLeg.not_specified,
        server_default=StrongLeg.not_specified.value,
        nullable=True,
    )
    player_role_id: Mapped[int] = mapped_column(
        ForeignKey("player_roles.id", onupdate="SET NULL", ondelete="SET NULL"),
        nullable=True,
        default=1,  # Значення за замовчуванням на рівні Python-коду
        server_default="1",  # Значення за замовчуванням на рівні бази даних
    )
    position_id: Mapped[int] = mapped_column(
        ForeignKey("positions.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )
    team_person_id: Mapped[int] = mapped_column(
        ForeignKey(
            "team_person_association.id", onupdate="CASCADE", ondelete="CASCADE"
        ),
        nullable=False,
    )
    # зв'язки з таблицями
    player_role: Mapped["PlayerRole"] = relationship(
        back_populates="positions_role",
    )
    team_person: Mapped["TeamPerson"] = relationship(
        back_populates="positions_role",
    )
    position: Mapped["Position"] = relationship(
        back_populates="positions_role",
    )
    match_properties: Mapped["MatchProperties"] = relationship(
        back_populates="player",
    )


# Функція для оновлення поля enddate, якщо active = 1
def update_enddate(mapper, connection, target):
    if target.active:
        target.enddate = int(datetime.utcnow().timestamp())


# Додаємо слухачі подій для вставки та оновлення
event.listen(PositionRole, "before_insert", update_enddate)
event.listen(PositionRole, "before_update", update_enddate)
