from datetime import date
from pydantic import BaseModel, ConfigDict
from typing import Optional, Annotated
from annotated_types import MinLen, MaxLen

from models.match import MatchStatus


class MatchBaseSchemas(BaseModel):
    event: Optional[date | None] = None
    season_id: Optional[int | None] = None
    group_id: Optional[int | None] = None
    round: Annotated[str, MaxLen(20)]
    stadium_id: Optional[int | None] = None
    team1_id: Optional[int]
    team1_goals: Optional[int | None] = None
    team2_goals: Optional[int | None] = None
    team2_id: Optional[int]
    status: MatchStatus
    standing: bool = 1


class MatchCreateSchemas(MatchBaseSchemas):
    status: MatchStatus = MatchStatus.not_played
    # pass


class MatchUpdateSchemas(MatchBaseSchemas):
    pass


class MatchSchemas(MatchBaseSchemas):
    model_config = ConfigDict(from_attributes=True)

    id: int
