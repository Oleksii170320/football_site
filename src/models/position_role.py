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

metadata = MetaData()


class TypeRole(str, Enum):
    goalkeeper = "Воротар"
    back = "Захисник"
    half_back = "Півзахисник"
    forward = "Нападник"
    universal = "Універсал"
    not_specified = "---"


class StrongLeg(str, Enum):
    only_rights = "Тільки права"
    right = "Зправа"
    only_left = "Тільки ліва"
    left = "Зліва"
    both = "Обидві"
    not_specified = "---"


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
    type_role = Column(
        SQLAlchemyEnum(TypeRole),
        default=TypeRole.not_specified,
        server_default=TypeRole.not_specified.value,
        nullable=True,
    )
    strong_leg = Column(
        SQLAlchemyEnum(StrongLeg),
        default=StrongLeg.not_specified,
        server_default=StrongLeg.not_specified.value,
        nullable=True,
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

    team_person: Mapped["TeamPerson"] = relationship(
        back_populates="positions_role",
    )
    position: Mapped["Position"] = relationship(
        back_populates="positions_role",
    )


# Функція для оновлення поля enddate, якщо active = 1
def update_enddate(mapper, connection, target):
    if target.active:
        target.enddate = int(datetime.utcnow().timestamp())


# Додаємо слухачі подій для вставки та оновлення
event.listen(PositionRole, "before_insert", update_enddate)
event.listen(PositionRole, "before_update", update_enddate)
