from datetime import date
from pydantic import BaseModel, ConfigDict
from typing import Optional, Annotated


class MatchPropertiesBaseSchemas(BaseModel):
    protocol: bool = 1
    starting: bool = 0
    replacement: bool = 0
    minutes: Optional[int | None] = None
    goals: Optional[int | None] = None
    goals_penalty: Optional[int | None] = None
    yellow_card: bool = 0
    second_yellow_card: bool = 0
    red_card: bool = 0
    match_id: int
    player_id: int
    # person_id: int


class MatchPropertiesCreateSchemas(MatchPropertiesBaseSchemas):
    pass


class MatchPropertiesUpdateSchemas(MatchPropertiesBaseSchemas):
    pass


class MatchPropertiesSchemas(MatchPropertiesBaseSchemas):
    model_config = ConfigDict(from_attributes=True)

    id: int
