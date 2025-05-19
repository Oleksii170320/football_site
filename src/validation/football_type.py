from pydantic import BaseModel, ConfigDict
from typing import Optional, Annotated
from annotated_types import MinLen, MaxLen

from validation.tournament import TournamentSchemas


class FootbalTypeBaseSchemas(BaseModel):
    name: Annotated[str, MinLen(1), MaxLen(50)]
    emblem: Annotated[Optional[str], MaxLen(256)] = None
    slug: str


class GroupCreateSchemas(FootbalTypeBaseSchemas):
    pass


class GroupUpdateSchemas(FootbalTypeBaseSchemas):
    pass


class GroupSchemas(FootbalTypeBaseSchemas):
    model_config = ConfigDict(from_attributes=True)

    id: int
    matches: Optional[list["TournamentSchemas"]] = []
