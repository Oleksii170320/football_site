from typing import TYPE_CHECKING, Optional, Annotated
from pydantic import BaseModel, ConfigDict
from annotated_types import MinLen, MaxLen

from .group import GroupSchemas

if TYPE_CHECKING:
    from .team import TeamSchemas
    from .match import MatchSchemas


class SeasonBaseSchemas(BaseModel):
    name: Annotated[str, MinLen(1), MaxLen(70)]
    start_date: int  # Зміна на EPOCH
    end_date: int  # Зміна на EPOCH
    year: Annotated[Optional[str], MaxLen(20)] = None
    standing: bool = 1
    slug: Annotated[str, MinLen(1), MaxLen(100)]
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
    # matches: list["MatchSchemas"] = []
    # groups: Optional[list["GroupSchemas"]] = []
