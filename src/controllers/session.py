from datetime import datetime, timedelta

from cryptography.fernet import Fernet
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import RedirectResponse

from core.database import get_db
from core.templating import render
from helpers.authentications import get_current_user_for_button
from services import get_regions_list
from services.users import authenticate_user, get_user_by_username, add_new_user
import validation.users as schema


router = APIRouter()

# Генерація ключа (тільки один раз і зберігається безпечно)
key = Fernet.generate_key()
cipher_suite = Fernet(key)


@router.get("/")
async def signInPage(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user_for_button),
):
    user_session, is_authenticated = current_user

    return render(
        "session/login.html",
        request,
        {
            "regions_list": await get_regions_list(db),  # Список регіонів (бокове меню)
            "is_authenticated": is_authenticated,  # Передаємо значення
            "user_session": user_session,  # Ім'я користувача
        },
    )


@router.post("/")
async def login(
    request: Request,
    db: AsyncSession = Depends(get_db),
    username: str = Form(...),
    password: str = Form(...),
):
    """Create new user-admin at the site"""

    now = datetime.now()
    midnight = (now + timedelta(days=1)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    seconds_until_midnight = int((midnight - now).total_seconds())

    # Перевірка даних користувача
    user = await authenticate_user(db, username, password)
    if not user:
        raise HTTPException(status_code=401, detail="Невірний логін або пароль")

    # Шифрування значення
    encrypted_token = cipher_suite.encrypt(user.username.encode())

    # Якщо авторизація успішна, можна зберегти інформацію про сесію або створити токен
    response = RedirectResponse(url="/", status_code=302)
    response.set_cookie(
        key="auth_token",
        value=encrypted_token.decode(),  # Зберігаємо зашифроване значення
        max_age=seconds_until_midnight,
        secure=True,
        httponly=True,
    )
    return response


@router.post("/register/")
async def register_user(
        user: schema.UserCreate,
        db: AsyncSession = Depends(get_db)
):
    # Перевірка, чи існує користувач з таким ім'ям
    existing_user = await get_user_by_username(db, user.username)
    if existing_user:
        raise HTTPException(
            status_code=400, detail="Користувач з таким ім'ям вже існує"
        )

    # Додавання нового користувача
    new_user = await add_new_user(
        db, user.username, user.password, user.email, user.full_name
    )
    return {"msg": "Користувача успішно створено", "user": new_user}
