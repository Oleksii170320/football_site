from datetime import date, datetime
from pydantic import BaseModel, ConfigDict, validator
from typing import Optional


from models.match import MatchStatus


class MatchBaseSchemas(BaseModel):
    event: int = 4102437600
    season_id: int
    group_id: Optional[int | None] = None
    stage_id: Optional[int | None] = None
    round_id: Optional[int | None] = None
    stadium_id: Optional[int | None] = None
    team1_id: int
    team1_goals: Optional[int | None] = None
    team2_goals: Optional[int | None] = None
    team2_id: int
    standing: bool = 1
    team1_penalty: Optional[int | None] = None
    team2_penalty: Optional[int | None] = None
    status: MatchStatus
    standing: bool = 1
    match_info: str = None
    match_video: str = None


class MatchCreateSchemas(MatchBaseSchemas):
    status: MatchStatus = MatchStatus.not_played

    @validator("team1_goals", "team2_goals", "team1_penalty", "team2_penalty")
    def validate_scores(cls, value):
        if value is not None and value < 0:
            raise ValueError("Голи та пенальті не можуть бути від’ємними")
        return value


class MatchUpdateSchemas(MatchBaseSchemas):
    pass


class MatchSchemas(MatchBaseSchemas):
    model_config = ConfigDict(from_attributes=True)

    id: int
    # players: list["PersonSchemas"] = []
