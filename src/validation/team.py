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
    foundation_year: Optional[str]
    logo: Optional[str]
    description: Optional[str]
    clubs_site: Optional[str]
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
    matches_1: List["MatchSchemas"] = []
    matches_2: List["MatchSchemas"] = []
    persons: List["PersonSchemas"] = []
