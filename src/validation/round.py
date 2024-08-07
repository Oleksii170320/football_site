from pydantic import BaseModel, ConfigDict
from typing import Optional, Annotated
from annotated_types import MinLen, MaxLen

from .match import MatchSchemas


class RoundBaseSchemas(BaseModel):
    name: Annotated[str, MinLen(1), MaxLen(50)]
    slug: str


class RoundCreateSchemas(RoundBaseSchemas):
    pass


class RoundUpdateSchemas(RoundBaseSchemas):
    pass


class RoundSchemas(RoundBaseSchemas):
    model_config = ConfigDict(from_attributes=True)

    id: int
    matches: Optional[list["MatchSchemas"]] = []
