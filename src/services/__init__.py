from fastapi import Request

from core.database import get_db
from core.sessions import get_session
from .match import get_season_matches_weeks
from .region import get_regions, get_region, get_region_seasons, get_regions_list
from .season import get_seasons_region, get_season_by_id_or_slug
from .tournament import get_tournament_for_season


FUNCTIONS = {
    "regions_list": get_regions_list,  # Список регіонів (бокове меню)
    "seasons": get_seasons_region,
    "region": get_regions,
    "season": get_season_by_id_or_slug,
    "tournaments": get_tournament_for_season,
    "matches": get_season_matches_weeks,
}


def get_user(request: Request):
    session = get_session(request)
    user = session.get("user")
    return user


def get_context_data(request: Request, fields, *args, **kwargs):
    user = get_user(request)
    db = next(get_db())
    context = {"user": user}
    for field in fields:
        context[field] = FUNCTIONS[field](db, *args, **kwargs)

    return context
