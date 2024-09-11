from enum import Enum
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Annotated
from annotated_types import MinLen, MaxLen

from models.stadium import TypeCoverage
from validation.team import TeamSchemas
from validation.match import MatchSchemas


class StadiumBaseSchemas(BaseModel):
    name: Annotated[str, MinLen(1), MaxLen(70)]
    city: Annotated[Optional[str], MaxLen(70)]
    address: Annotated[Optional[str], MaxLen(200)]
    photo: Annotated[Optional[str], MaxLen(256)]
    capacity: Annotated[Optional[str], MaxLen(30)]
    dimensions: Annotated[Optional[str], MaxLen(20)]
    type_coverage: TypeCoverage
    region_id: Optional[int]


class StadiumCreateSchemas(StadiumBaseSchemas):
    type_coverage: TypeCoverage = TypeCoverage.not_specified.value
    # pass


class StadiumUpdateSchemas(StadiumBaseSchemas):
    pass


class StadiumSchemas(StadiumBaseSchemas):
    model_config = ConfigDict(from_attributes=True)

    id: int
    teams: list["TeamSchemas"] = []
    matches: list["MatchSchemas"] = []
