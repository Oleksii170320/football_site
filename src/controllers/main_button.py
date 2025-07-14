from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from core.templating import render
from core.database import get_db
from helpers.authentications import get_current_user_for_button
from services import get_regions_list
from services.matches.matches_for_region import get_matches_week
from services.news_list import get_news_list

router = APIRouter()


@router.get("/matches")
async def get_weekly_matches(
        request: Request,
        db: AsyncSession = Depends(get_db),
        current_user: str = Depends(get_current_user_for_button),
):

    user_session, is_authenticated = current_user
    return render(
        "home.html",
        request,
        {
            "matches": await get_matches_week(db),  # Всі матчі +/- 7 днів (всі тірніри свйту)
            "regions_list": await get_regions_list(db),  # Список регіонів (бокове меню)
            "is_authenticated": is_authenticated,  # Передаємо значення
            "user_session": user_session,  # Ім'я користувача
        },
    )


@router.get("/news")
async def get_all_news(
        request: Request,
        db: AsyncSession = Depends(get_db),
        current_user: str = Depends(get_current_user_for_button),
):
    user_session, is_authenticated = current_user

    return render(
        "home.html",
        request,
        {
            "news_list": await get_news_list(db),  # Стрічка новин (всі регіони)
            "regions_list": await get_regions_list(db),  # Список регіонів (бокове меню)
            "is_authenticated": is_authenticated,  # Передаємо значення
            "user_session": user_session,  # Ім'я користувача
        },
    )


@router.get("/about")
async def get_main_about_information(
        request: Request,
        db: AsyncSession = Depends(get_db),
        current_user: str = Depends(get_current_user_for_button),
):
    user_session, is_authenticated = current_user

    return render(
        "home.html",
        request,
        {
            "about": True,
            "regions_list": await get_regions_list(db),  # Список регіонів (бокове меню)
            "is_authenticated": is_authenticated,  # Передаємо значення
            "user_session": user_session,  # Ім'я користувача
        },
    )


@router.get("/contacts")
async def get_main_contacts(
        request: Request,
        db: AsyncSession = Depends(get_db),
        current_user: str = Depends(get_current_user_for_button),
):
    user_session, is_authenticated = current_user

    return render(
        "home.html",
        request,
        {
            "contacts": True,
            "regions_list": await get_regions_list(db),  # Список регіонів (бокове меню)
            "is_authenticated": is_authenticated,  # Передаємо значення
            "user_session": user_session,  # Ім'я користувача
        },
    )