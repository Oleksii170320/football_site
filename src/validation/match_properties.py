from datetime import date
from pydantic import BaseModel, ConfigDict
from typing import Optional, Annotated

from validation.match_event import MatchEventSchemas


class MatchPropertiesBaseSchemas(BaseModel):
    protocol: bool = 1
    starting: bool = 0
    start_min: Optional[int | None] = None
    end_min: Optional[int | None] = None
    match_id: int
    player_id: int


class MatchPropertiesCreateSchemas(MatchPropertiesBaseSchemas):
    pass


class MatchPropertiesUpdateSchemas(MatchPropertiesBaseSchemas):
    pass


class MatchPropertiesSchemas(MatchPropertiesBaseSchemas):
    model_config = ConfigDict(from_attributes=True)

    id: int
    matches_event: list[MatchEventSchemas] = []
    matches_replacement: Optional[list[MatchEventSchemas]] = []
