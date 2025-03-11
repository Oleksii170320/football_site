from sqlalchemy import String
from sqlalchemy.orm import relationship, mapped_column, Mapped

from core.database import Base
from models.annonated import intpk


class FootbalType(Base):
    __tablename__ = "football_types"

    id: Mapped[intpk]
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    emblem: Mapped[str | None] = mapped_column(String(256))
    slug: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)

    # зв'язки з таблицями
    tournaments: Mapped[list["Tournament"]] = relationship(
        back_populates="football_types",
    )
