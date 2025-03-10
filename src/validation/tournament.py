from pydantic import BaseModel, ConfigDict
from typing import Optional, Annotated
from annotated_types import MinLen, MaxLen

from models.tournament import FootballType
from validation.season import SeasonSchemas


class TournamentBaseSchemas(BaseModel):
    name: Annotated[str, MinLen(1), MaxLen(70)]
    full_name: Annotated[str, MinLen(1), MaxLen(100)]
    logo: Annotated[Optional[str], MaxLen(256)] = None
    description: str = None
    football_type: FootballType
    website: Optional[str] = None
    page_facebook: Optional[str] = None
    page_youtube: Optional[str] = None
    page_telegram: Optional[str] = None
    page_instagram: Optional[str] = None
    level_int: Optional[int | None] = None
    level: Optional[str | None] = None
    level_up: Optional[str | None] = None
    level_down: Optional[str | None] = None
    create_year: Optional[str | None] = None
    organization_id: int
    football_type_id: int


class TournamentCreateSchemas(TournamentBaseSchemas):
    # football_type: FootballType = FootballType.football
    pass


class TournamentUpdateSchemas(TournamentBaseSchemas):
    pass


class TournamentSchemas(TournamentBaseSchemas):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    seasons: Optional[list[SeasonSchemas]] = []
    # newstables: Optional[list[NewsTableSchemas]] = []
