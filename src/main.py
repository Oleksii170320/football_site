from typing import List

from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from core.database import get_db
from core.templating import templates
from services.news_list import get_news_list
from services.region import get_regions_list
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
    api,
)
from services.team import get_teams_in_season
from validation.team import TeamSchemas

app = FastAPI(title="Football")

# Підключення статичних файлів
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", tags=["Home"])
async def home(request: Request, db: AsyncSession = Depends(get_db)):

    return templates.TemplateResponse(
        "home.html",
        {
            "request": request,
            "news_list": await get_news_list(db),  # Стрічка новин (всі регіони)
            "regions_list": await get_regions_list(db),  # Список регіонів (бокове меню)
        },
    )


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
app.include_router(api.router, prefix="/api", tags=["API"])
app.include_router(session.router, prefix="/sign-in", tags=["Auth"])
