from datetime import date

from pydantic import BaseModel, ConfigDict
from typing import Optional, Annotated
from annotated_types import MinLen, MaxLen

from validation.match_properties import MatchPropertiesSchemas


class PersonBaseSchemas(BaseModel):
    name: Annotated[str, MinLen(1), MaxLen(30)]
    surname: Annotated[str, MinLen(1), MaxLen(30)] = None
    lastname: Annotated[str, MinLen(1), MaxLen(40)] = None
    photo: Annotated[str, MaxLen(256)] = None
    birthday: Optional[date | None] = None
    region_id: Optional[int]


class PersonCreateSchemas(PersonBaseSchemas):
    pass


class PersonUpdateSchemas(PersonBaseSchemas):
    pass


class PersonSchemas(PersonBaseSchemas):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    teams: list["TeamSchemas"] = []
    team_president: list["TeamSchemas"] = []
    team_coach: list["TeamSchemas"] = []
    # match_properties: list["MatchPropertiesSchemas"] = []
