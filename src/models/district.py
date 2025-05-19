from typing import TYPE_CHECKING
from sqlalchemy import String, UniqueConstraint, ForeignKey
from sqlalchemy.orm import relationship, mapped_column, Mapped
from sqlalchemy.ext.declarative import declared_attr

from core.database import Base
from models.annonated import intpk
from slugify import slugify

# if TYPE_CHECKING:
#     from models.organization import Organization
#     from models.team import Team
#     from models.stadium import Stadium
#     from models.person import Person
#     from models.news import News
#
#     from models.contacts import Contact


class District(Base):
    __tablename__ = "districts"

    _region_id_nullable: bool = True
    _region_id_unique: bool = False
    _region_back_populates = "districts"

    id: Mapped[intpk]
    name: Mapped[str] = mapped_column(String(30), nullable=False)
    emblem: Mapped[str | None] = mapped_column(String(256))
    slug: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)

    # зовнішні ключі
    region_id: Mapped[int | None] = mapped_column(
        ForeignKey("organizations.id", onupdate="SET NULL", ondelete="SET NULL"),
    )

    @declared_attr
    def __mapper_args__(cls):
        return {"confirm_deleted_rows": False}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if "slug" not in kwargs and "name" in kwargs:
            self.slug = self.generate_slug(kwargs["name"])

    def generate_slug(self, name: str) -> str:
        return slugify(f"{name}")
