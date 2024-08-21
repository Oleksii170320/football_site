from pydantic import BaseModel, ConfigDict
from typing import Annotated
from annotated_types import MinLen, MaxLen

from validation.position_role import PositionRoleSchemas


class PlayerRoleBaseSchemas(BaseModel):
    full_name: Annotated[str, MinLen(1), MaxLen(20)]
    name: Annotated[str, MinLen(1), MaxLen(3)]
    full_futzal_name: Annotated[str, MinLen(1), MaxLen(20)]
    futzal_name: Annotated[str, MinLen(1), MaxLen(3)]
    slug: Annotated[str, MinLen(1), MaxLen(5)]


class PlayerRoleCreateSchemas(PlayerRoleBaseSchemas):
    pass


class PlayerRoleUpdateSchemas(PlayerRoleBaseSchemas):
    pass


class PlayerRoleSchemas(PlayerRoleBaseSchemas):
    model_config = ConfigDict(from_attributes=True)

    id: int
    positions_role: list["PositionRoleSchemas"] = []
