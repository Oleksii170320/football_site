from pydantic import BaseModel, ConfigDict
from typing import Annotated


class TeamSeasonSchemas(BaseModel):
    team_id: Annotated[int]
    season_id: Annotated[int]


class TeamSeasonCreateSchemas(TeamSeasonSchemas):
    pass


class TeamSeasonUpdateSchemas(TeamSeasonSchemas):
    pass


class TeamSeasonSchemas(TeamSeasonSchemas):
    model_config = ConfigDict(from_attributes=True)

    id: int
