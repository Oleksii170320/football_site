from datetime import date

from pydantic import BaseModel, ConfigDict
from typing import Optional, Annotated
from annotated_types import MinLen, MaxLen

from models.position_role import StrongLeg
from validation.match_properties import MatchPropertiesSchemas


class PositionRoleBaseSchemas(BaseModel):
    team_person_id: Annotated[int]
    position_id: Annotated[Optional[int]]
    strong_leg: StrongLeg
    player_number: Optional[int | None]
    startdate: Optional[date | None] = None
    enddate: Optional[date | None] = None
    standing: bool = 1
    player_role_id: Annotated[int] = 1


class PositionRoleCreateSchemas(PositionRoleBaseSchemas):
    strong_leg: StrongLeg = StrongLeg.not_specified
    # pass


class PositionRoleUpdateSchemas(PositionRoleBaseSchemas):
    pass


class PositionRoleSchemas(PositionRoleBaseSchemas):
    model_config = ConfigDict(from_attributes=True)

    id: int
    match_properties: list["MatchPropertiesSchemas"] = []
