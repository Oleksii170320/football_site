from pydantic import BaseModel, ConfigDict
from typing import Optional, Annotated
from annotated_types import MinLen, MaxLen


class DistrictBaseSchemas(BaseModel):
    name: Annotated[str, MinLen(3), MaxLen(30)]
    emblem: Annotated[Optional[str], MaxLen(30)] = None
    slug: Annotated[Optional[str], MaxLen(30)]
    region_id: int


class DistrictCreateSchemas(DistrictBaseSchemas):
    pass


class DistrictUpdateSchemas(DistrictBaseSchemas):
    pass


class DistrictSchemas(DistrictBaseSchemas):
    model_config = ConfigDict(from_attributes=True)

    id: int
