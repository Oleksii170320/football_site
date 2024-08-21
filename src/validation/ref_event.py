from pydantic import BaseModel, ConfigDict
from typing import Optional, Annotated
from annotated_types import MinLen, MaxLen

from validation.match_event import MatchEventSchemas


class RefEventBaseSchemas(BaseModel):
    name: Annotated[str, MinLen(1), MaxLen(35)]
    slug: Annotated[str, MinLen(1), MaxLen(40)]
    image: Annotated[str, MaxLen(256)]


class RefEventCreateSchemas(RefEventBaseSchemas):
    pass


class RefEventUpdateSchemas(RefEventBaseSchemas):
    pass


class RefEventSchemas(RefEventBaseSchemas):
    model_config = ConfigDict(from_attributes=True)

    id: int
    matches_event: Optional[list[MatchEventSchemas]] = []
