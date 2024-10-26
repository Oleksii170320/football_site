from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, Request, Form, Response
from fastapi.responses import RedirectResponse

from core.database import get_db
from core.templating import render
from services import get_regions_list
from services.users import authenticate_user, get_user_by_username, add_new_user
import validation.users as schema


router = APIRouter()


@router.get("/")
async def signInPage(request: Request, db: AsyncSession = Depends(get_db)):

    regions_list = await get_regions_list(db)  # Асинхронний виклик
    return render(
        "session/login.html",
        request,
        {
            "regions_list": regions_list,  # Список регіонів (бокове меню)
        },
    )


@router.post("/")
async def login(
    request: Request,
    db: AsyncSession = Depends(get_db),
    username: str = Form(...),
    password: str = Form(...),
):
    now = datetime.now()
    midnight = (now + timedelta(days=1)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    seconds_until_midnight = int((midnight - now).total_seconds())

    # Перевірка даних користувача
    user = await authenticate_user(db, username, password)
    if not user:
        raise HTTPException(status_code=401, detail="Невірний логін або пароль")

    # Якщо авторизація успішна, можна зберегти інформацію про сесію або створити токен
    response = RedirectResponse(url="/", status_code=302)
    response.set_cookie(
        key="username",
        value=f"{user.username}",
        max_age=seconds_until_midnight,
        secure=True,
        httponly=True,
    )
    return response


@router.post("/register/")
async def register_user(user: schema.UserCreate, db: AsyncSession = Depends(get_db)):
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
