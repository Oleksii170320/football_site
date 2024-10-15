from typing import Annotated, List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from fastapi import APIRouter, Depends, HTTPException, Request, Form, Response
from fastapi.responses import RedirectResponse

from core.database import get_db
from core.sessions import get_session
from core.templating import templates, render
from services import get_regions_list, get_seasons_region
from services.users import authenticate

# from validation.users import UserSchemas

router = APIRouter()


# @router.get("/")
# def signInPage(request: Request, db: Session = Depends(get_db)):
#     return templates.TemplateResponse(
#         "session/login.html",
#         {
#             "request": request,
#             "regions_list": get_regions_list(db),  # Список регіонів (бокове меню)
#         },
#     )


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


# @router.post("/", response_model=List[UserSchemas])
# def authenticate_user(
#     request: Request,
#     response: Response,
#     username: Annotated[str, Form()],
#     email: Annotated[str, Form()],
#     password_hash: Annotated[str, Form()],
#     db: Session = Depends(get_db),
# ):
#     if user := authenticate(username, email, password_hash):
#         session = get_session(request)
#         session["user"] = user
#         return RedirectResponse("/")
#     else:
#         return templates.TemplateResponse(
#             "session/login.html",
#             {
#                 "request": request,
#                 "regions_list": get_regions_list(db),  # Список регіонів (бокове меню)
#                 "error": "wrong username or password",
#             },
#         )


@router.post(
    "/"
    # , response_model=List[UserSchemas]
)
async def authenticate_user(
    request: Request,
    response: Response,
    username: str = Form(...),
    email: str = Form(...),
    password_hash: str = Form(...),
    db: AsyncSession = Depends(get_db),
):
    # Використовуйте асинхронні виклики для аутентифікації
    if user := await authenticate(
        username, email, password_hash
    ):  # Припускаємо, що authenticate асинхронна
        session = get_session(request)
        session["user"] = user
        return RedirectResponse("/")
    else:
        regions_list = await get_regions_list(db)  # Виклик асинхронної функції
