from pydantic import BaseModel, ConfigDict
from typing import Optional, Annotated
from annotated_types import MinLen, MaxLen

from .match import MatchSchemas


class StageBaseSchemas(BaseModel):
    name: Annotated[str, MinLen(1), MaxLen(50)]
    slug: str


class StageCreateSchemas(StageBaseSchemas):
    pass


class StageUpdateSchemas(StageBaseSchemas):
    pass


class StageSchemas(StageBaseSchemas):
    model_config = ConfigDict(from_attributes=True)

    id: int
    matches: Optional[list["MatchSchemas"]] = []
