from pydantic import BaseModel, ConfigDict
from typing import Optional, Annotated
from annotated_types import MinLen, MaxLen

from models.organization import TournamentLevel
from validation.tournament import TournamentSchemas


class OrganizationBaseSchemas(BaseModel):
    name: Annotated[str, MinLen(1), MaxLen(10)]
    full_name: Annotated[str, MinLen(1), MaxLen(70)]
    description: Optional[str] = None
    logo: Annotated[Optional[str], MaxLen(256)] = None
    website: Annotated[Optional[str], MaxLen(256)] = None
    tournament_level: TournamentLevel
    region_id: int
    association_id: int


class OrganizationCreateSchemas(OrganizationBaseSchemas):
    tournament_level: TournamentLevel = TournamentLevel.not_specified
    pass


class OrganizationUpdateSchemas(OrganizationBaseSchemas):
    pass


class OrganizationSchemas(OrganizationBaseSchemas):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    tournaments: Optional[list["TournamentSchemas"]] = []
