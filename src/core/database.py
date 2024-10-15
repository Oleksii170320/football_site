from typing import AsyncGenerator

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from config import SQLALCHEMY_DATABASE_URL

# Додайте префікс "sqlite+aiosqlite://" до URL бази даних
SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

# SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace(
#     "sqlite:///", "sqlite+aiosqlite:///"
# )

# Асинхронний двигун SQLAlchemy для SQLite
engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=False)


AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Базовий клас для моделей
Base = declarative_base()


# Залежність для отримання асинхронної сесії БД
async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as db:
        yield db


# Модифікована модель з методом to_dict
class Base(declarative_base()):
    __abstract__ = True

    def to_dict(self):
        return {field.name: getattr(self, field.name) for field in self.__table__.c}
