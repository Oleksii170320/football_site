from pydantic import BaseModel, ConfigDict
from typing import Annotated, Optional
from annotated_types import MaxLen


class MatchEventBaseSchemas(BaseModel):
    player_match_id: int
    event_id: int
    minute: Annotated[str, MaxLen(10)]
    player_replacement_id: Optional[int] = None


class MatchEventCreateSchemas(MatchEventBaseSchemas):
    pass


class MatchEventUpdateSchemas(MatchEventBaseSchemas):
    pass


class MatchEventSchemas(MatchEventBaseSchemas):
    model_config = ConfigDict(from_attributes=True)

    id: int
