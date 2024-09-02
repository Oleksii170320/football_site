from pydantic import BaseModel, ConfigDict
from typing import Optional, Annotated
from annotated_types import MaxLen


class ContactBaseSchemas(BaseModel):
    telephone: Annotated[Optional[str], MaxLen(20)] = None
    address: Annotated[Optional[str], MaxLen(256)] = None
    email: Annotated[Optional[str], MaxLen(70)] = None
    region_id: int


class ContactCreateSchemas(ContactBaseSchemas):
    pass


class ContactUpdateSchemas(ContactBaseSchemas):
    pass


class ContactSchemas(ContactBaseSchemas):
    model_config = ConfigDict(from_attributes=True)

    id: int
