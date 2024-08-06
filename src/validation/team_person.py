from pydantic import BaseModel, ConfigDict
from typing import Annotated

from validation.position_role import PositionRoleSchemas


class TeamPersonSchemas(BaseModel):
    team_id: Annotated[int]
    person_id: Annotated[int]


class TeamPersonCreateSchemas(TeamPersonSchemas):
    pass


class TeamPersonUpdateSchemas(TeamPersonSchemas):
    pass


class TeamPersonSchemas(TeamPersonSchemas):
    model_config = ConfigDict(from_attributes=True)

    id: int
    positions_role: list["PositionRoleSchemas"] = []
