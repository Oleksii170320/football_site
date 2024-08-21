from typing import TYPE_CHECKING
from sqlalchemy import String, Index, UniqueConstraint
from sqlalchemy.orm import relationship, mapped_column, Mapped
from sqlalchemy.ext.declarative import declared_attr

from core.database import Base
from models.annonated import intpk
from slugify import slugify

if TYPE_CHECKING:
    from models.position_role import PositionRole


class PlayerRole(Base):
    __tablename__ = "player_roles"

    id: Mapped[intpk]
    full_name: Mapped[str] = mapped_column(String(20), nullable=False)
    name: Mapped[str] = mapped_column(String(3), nullable=False)
    full_futzal_name: Mapped[str] = mapped_column(String(20), nullable=False)
    futzal_name: Mapped[str] = mapped_column(String(3), nullable=False)
    slug: Mapped[str] = mapped_column(String, nullable=False)

    # зв'язки з таблицями
    positions_role: Mapped["PositionRole"] = relationship(
        back_populates="player_role",
    )
