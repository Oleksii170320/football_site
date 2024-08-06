from typing import TYPE_CHECKING
from pydantic import BaseModel, ConfigDict
from typing import Optional, Annotated
from annotated_types import MinLen, MaxLen
from datetime import date

from .group import GroupSchemas

if TYPE_CHECKING:
    from .team import TeamSchemas
    from .match import MatchSchemas


class SeasonBaseSchemas(BaseModel):
    name: Annotated[str, MinLen(1), MaxLen(70)]
    start_date: date
    end_date: date
    year: Annotated[Optional[str], MaxLen(20)] = None
    standing: bool = 1
    slug: Annotated[str, MinLen(1), MaxLen(70)]
    tournament_id: int
    team_winner_id: Optional[int] = None


class SeasonCreateSchemas(SeasonBaseSchemas):
    pass


class SeasonUpdateSchemas(SeasonBaseSchemas):
    pass


class SeasonSchemas(SeasonBaseSchemas):
    model_config = ConfigDict(from_attributes=True)

    id: int
    teams: list["TeamSchemas"] = []
    matches: list["MatchSchemas"] = []
    groups: Optional[list["GroupSchemas"]] = []
