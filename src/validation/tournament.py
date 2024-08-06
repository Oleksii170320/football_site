from pydantic import BaseModel, ConfigDict
from typing import Optional, Annotated
from annotated_types import MinLen, MaxLen

from validation.news import NewsTableSchemas
from validation.season import SeasonSchemas


class TournamentBaseSchemas(BaseModel):
    name: Annotated[str, MinLen(1), MaxLen(70)]
    full_name: Annotated[str, MinLen(1), MaxLen(100)]
    logo: Annotated[Optional[str], MaxLen(256)] = None
    description: str = None
    football_type: Annotated[Optional[str], MaxLen(25)] = None
    website: Optional[str] = None
    organization_id: int


class TournamentCreateSchemas(TournamentBaseSchemas):
    pass


class TournamentUpdateSchemas(TournamentBaseSchemas):
    pass


class TournamentSchemas(TournamentBaseSchemas):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    seasons: Optional[list[SeasonSchemas]] = []
    newstables: Optional[list[NewsTableSchemas]] = []
