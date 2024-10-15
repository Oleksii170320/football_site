# from datetime import datetime
# from sqlalchemy import String, Boolean, DateTime, JSON, TIMESTAMP, Integer, ForeignKey
# from sqlalchemy.orm import mapped_column, Mapped
# from core.database import Base
# from models.annonated import intpk
#
#
# class Role(Base):
#     __tablename__ = "role"
#
#     id: Mapped[int] = mapped_column(primary_key=True)
#     name: Mapped[str] = mapped_column(String(150), nullable=False)
#     permissions: Mapped[dict] = mapped_column(JSON)
#
#
# class User(Base):
#     __tablename__ = "users"
#
#     id: Mapped[int] = mapped_column(primary_key=True)
#     email: Mapped[str] = mapped_column(String(255), nullable=False)
#     username: Mapped[str] = mapped_column(String(150), nullable=False)
#     register_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.utcnow)
#     password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
#     role_id: Mapped[int] = mapped_column(Integer, ForeignKey("role.id"))
#     is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
#     is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
#     is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
