from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship

from core.database import Base
from models.annonated import intpk
from models.region import Region


class Contact(Base):
    __tablename__ = "contacts"

    id: Mapped[intpk]
    telephone: Mapped[str] = mapped_column(String(20), nullable=True)
    address: Mapped[str] = mapped_column(String(256), nullable=True)
    email: Mapped[str] = mapped_column(String(70), nullable=True)
    region_id: Mapped[int | None] = mapped_column(
        ForeignKey("regions.id", onupdate="SET NULL", ondelete="SET NULL"),
        nullable=True,
    )

    # зв'язки з таблицями
    region: Mapped["Region"] = relationship(
        back_populates="contact",
    )
