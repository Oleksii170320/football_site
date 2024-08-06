from pydantic import BaseModel, ConfigDict
from typing import Optional, Annotated
from annotated_types import MinLen, MaxLen

from validation.organization import OrganizationSchemas


class AssociationBaseSchemas(BaseModel):
    name: Annotated[str, MinLen(1), MaxLen(10)]
    full_name: Annotated[str, MinLen(1), MaxLen(70)]
    description: Optional[str] = None
    logo: Annotated[Optional[str], MaxLen(256)] = None
    website: Annotated[Optional[str], MaxLen(256)] = None


class AssociationCreateSchemas(AssociationBaseSchemas):
    pass


class AssociationUpdateSchemas(AssociationBaseSchemas):
    pass


class AssociationSchemas(AssociationBaseSchemas):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    organizations: Optional[list["OrganizationSchemas"]] = []
