from datetime import datetime

from pydantic import BaseModel, ConfigDict
from typing import Optional, Annotated


class NewsTableBaseSchemas(BaseModel):
    event: Optional[datetime | None] = None
    topic: str
    brief: str
    description: Optional[str] = None
    photo: Optional[str] = None
    region_id: int


class NewsTableCreateSchemas(NewsTableBaseSchemas):
    pass


class NewsTableUpdateSchemas(NewsTableBaseSchemas):
    pass


class NewsTableSchemas(NewsTableBaseSchemas):
    model_config = ConfigDict(from_attributes=True)

    id: int
