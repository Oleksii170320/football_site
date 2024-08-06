from pydantic import BaseModel, ConfigDict
from typing import Optional, Annotated
from annotated_types import MinLen, MaxLen

from validation.match import MatchSchemas


class GroupBaseSchemas(BaseModel):
    name: Annotated[str, MinLen(1), MaxLen(50)]
    season_id: Optional[int | None] = None


class GroupCreateSchemas(GroupBaseSchemas):
    pass


class GroupUpdateSchemas(GroupBaseSchemas):
    pass


class GroupSchemas(GroupBaseSchemas):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    matches: Optional[list["MatchSchemas"]] = []
