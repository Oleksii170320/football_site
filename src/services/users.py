from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


from models import User


# Налаштування для хешування паролів
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


async def create_user(
    db: AsyncSession,
    username: str,
    password_hash: str,
    email: str = None,
    full_name: str = None,
):
    new_user = User(
        username=username,
        password_hash=password_hash,
        email=email,
        full_name=full_name,
        is_active=True,
        is_superuser=False,
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


async def add_new_user(
    db: AsyncSession, username: str, password: str, email: str, full_name: str
):
    # Генерація хешу для пароля
    hashed_password = get_password_hash(password)

    # Додавання нового користувача
    user = await create_user(db, username, hashed_password, email, full_name)
    return user


async def get_user_by_username(db: AsyncSession, username: str):
    # Виконуємо запит, використовуючи select() для отримання користувача за username
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalars().first()  # Отримуємо перший результат, якщо він є
    return user


async def authenticate_user(db: AsyncSession, username: str, password: str):
    # Отримання користувача з бази даних
    user = await get_user_by_username(db, username)
    if not user:
        return None

    # Перевірка пароля
    if not pwd_context.verify(password, user.password_hash):
        return None

    return user
