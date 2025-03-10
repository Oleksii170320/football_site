from pydantic import BaseModel, ConfigDict
from typing import Optional, Annotated
from annotated_types import MinLen, MaxLen

from validation.news import NewsTableSchemas
from validation.organization import OrganizationSchemas
from validation.person import PersonSchemas
from validation.team import TeamSchemas
from validation.stadium import StadiumSchemas
from validation.contacts import ContactSchemas


class RegionBaseSchemas(BaseModel):
    name: Annotated[str, MinLen(3), MaxLen(30)]
    emblem: Annotated[Optional[str], MaxLen(30)] = None
    slug: Annotated[Optional[str], MaxLen(30)]
    status: bool = 0


class RegionCreateSchemas(RegionBaseSchemas):
    pass


class RegionUpdateSchemas(RegionBaseSchemas):
    pass


class RegionSchemas(RegionBaseSchemas):
    model_config = ConfigDict(from_attributes=True)

    id: int
    teams: Optional[list[TeamSchemas]] = []
    organizations: Optional[list[OrganizationSchemas]] = []
    stadiums: Optional[list[StadiumSchemas]] = []
    persons: Optional[list[PersonSchemas]] = []
    contact: Optional[list[ContactSchemas]] = []
    newstables: Optional[list[NewsTableSchemas]] = []
