from typing import TYPE_CHECKING
from pydantic import BaseModel, ConfigDict
from typing import Optional, Annotated
from annotated_types import MinLen, MaxLen

from validation.match import MatchSchemas
from validation.season import SeasonSchemas

# if TYPE_CHECKING:
#     from validation.season import SeasonSchemas


class TeamBaseSchemas(BaseModel):
    name: Annotated[str, MinLen(1), MaxLen(70)]
    full_name: Annotated[Optional[str], MaxLen(120)] = None
    city: Annotated[str, MaxLen(50)] = None
    foundation_year: Annotated[Optional[str], MaxLen(20)] = None
    logo: Annotated[Optional[str], MaxLen(256)] = None
    description: Optional[str] = None
    clubs_site: Optional[str] = None
    region_id: Optional[int | None] = None
    stadium_id: Optional[int | None] = None
    president_id: Optional[int | None] = None
    coach_id: Optional[int | None] = None


class TeamCreateSchemas(TeamBaseSchemas):
    pass


class TeamUpdateSchemas(TeamBaseSchemas):
    pass


class TeamSchemas(TeamBaseSchemas):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    # seasons: list["SeasonSchemas"] = []
    seasons_won: list["SeasonSchemas"] = []
    matches_1: list["MatchSchemas"] = []
    matches_2: list["MatchSchemas"] = []
    persons: list["PersonSchemas"] = []
