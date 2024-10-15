from fastapi import APIRouter, Depends, HTTPException, Request

router = APIRouter()


# @router.get("/{season_id}/{season_slug}", response_model=List[schemas.MatchSchemas])
# def read_standing(request: Request, season_id: int, db: Session = Depends(get_db)):
#
#     regions_list = get_regions_list(db)
#     # seasons_region = get_seasons_region(db, region_slug=region_slug)
#     standings = get_calculate_standings(db, season_id=season_id)
#
#     return templates.TemplateResponse(
#         "standings.html",
#         {
#             "request": request,
#             "regions_list": regions_list,  # Список регіонів (бокове меню)
#             # "seasons": seasons_region,  # Список цьогорічних турнірів
#             "standings": standings,
#         },
#     )
