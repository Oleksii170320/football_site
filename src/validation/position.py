from pydantic import BaseModel, ConfigDict
from typing import Annotated
from annotated_types import MinLen, MaxLen


class PositionBaseSchemas(BaseModel):
    position: Annotated[str, MinLen(1), MaxLen(40)]


class PositionCreateSchemas(PositionBaseSchemas):
    pass


class PositionUpdateSchemas(PositionBaseSchemas):
    pass


class PositionSchemas(PositionBaseSchemas):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
