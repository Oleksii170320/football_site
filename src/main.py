from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
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
)


app = FastAPI(title="Football")

# Підключення статичних файлів
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", tags=["Home"])
def home(request: Request, db: Session = Depends(get_db)):

    news_list = get_news_list(db)
    regions_list = get_regions_list(db)

    return templates.TemplateResponse(
        "home.html",
        {
            "request": request,
            "news_list": news_list,  # Стрічка новин (всі регіони)
            "regions_list": regions_list,  # Список регіонів (бокове меню)
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

# app.include_router(person.router, prefix="/persons", tags=["Persons"])
