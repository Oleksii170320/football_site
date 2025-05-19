from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict

from validation.match import MatchSchemas
from validation.person import PersonSchemas
from validation.season import SeasonSchemas


class TeamBaseSchemas(BaseModel):
    name: str
    city: str
    region_id: int
    full_name: Optional[str]
    slug: str
    foundation_year: Optional[str] = None
    logo: Optional[str] = None
    description: Optional[str] = None
    clubs_site: Optional[str] = None
    page_facebook: Optional[str] = None
    page_youtube: Optional[str] = None
    page_telegram: Optional[str] = None
    page_instagram: Optional[str] = None
    stadium_id: Optional[int] = 0
    president_id: Optional[int] = 0
    coach_id: Optional[int] = 0


class TeamCreateSchemas(TeamBaseSchemas):
    pass


class TeamUpdateSchemas(TeamBaseSchemas):
    pass


class TeamSchemas(TeamBaseSchemas):
    model_config = ConfigDict(from_attributes=True)

    id: int
    seasons_won: List["SeasonSchemas"] = []
    # seasons_won2: List["SeasonSchemas"] = []
    matches_1: List["MatchSchemas"] = []
    matches_2: List["MatchSchemas"] = []
    persons: List["PersonSchemas"] = []
