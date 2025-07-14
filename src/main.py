from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.templating import templates
from helpers.authentications import get_current_user_for_button
from services.matches.matches_for_region import get_matches_week
from services.news_list import get_news_list
from services.regions.region import get_regions_list
from controllers import (
    region,
    organization,
    tournament,
    season,
    team,
    stadium,
    match,
    standings,
    person,
    news,
    session,
    main_button,
)
from controllers.api import (
    seasons_api,
    regions_api,
    matches_api,
    teams_api,
)

app = FastAPI(title="Football")

# Підключення статичних файлів
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", tags=["Home"])
async def home(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user_for_button),
):
    user_session, is_authenticated = current_user

    return templates.TemplateResponse(
        "home.html",
        {
            "request": request,
            "news_list": await get_news_list(db),  # Стрічка новин (всі регіони)
            "regions_list": await get_regions_list(db),  # Список регіонів (бокове меню)
            "is_authenticated": is_authenticated,  # Передаємо значення
            "user_session": user_session,  # Ім'я користувача
        },
    )


app.include_router(main_button.router, prefix="", tags=["Main Buttons"])
app.include_router(region.router, prefix="/region", tags=["Regions"])
app.include_router(organization.router, prefix="/organizations", tags=["Organizations"])
app.include_router(tournament.router, prefix="/tournaments", tags=["Tournaments"])
app.include_router(season.router, prefix="/seasons", tags=["Seasons"])
app.include_router(team.router, prefix="/teams", tags=["Teams"])
app.include_router(stadium.router, prefix="/stadiums", tags=["Stadiums"])
app.include_router(match.router, prefix="/matches", tags=["Matches"])
app.include_router(standings.router, prefix="/standings", tags=["Standings"])
app.include_router(person.router, prefix="/persons", tags=["Persons"])
app.include_router(news.router, prefix="/news", tags=["News"])
app.include_router(seasons_api.router, prefix="/api/seasons", tags=["API"])
app.include_router(matches_api.router, prefix="/api/matches", tags=["API"])
app.include_router(regions_api.router, prefix="/api/regions", tags=["API"])
app.include_router(teams_api.router, prefix="/api/teams", tags=["API"])
app.include_router(session.router, prefix="/sign-in", tags=["Auth"])
