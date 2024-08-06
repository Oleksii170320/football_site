import time
from typing import Optional, Annotated

from sqlalchemy.orm import relationship, mapped_column, Mapped
from sqlalchemy import Column, Integer, String, Text, ForeignKey, text, func


intpk = Annotated[int, mapped_column(primary_key=True, index=True, autoincrement=True)]
created_at = Annotated[
    int,
    mapped_column(
        default=lambda: int(time.time()),
    ),
]
updated_at = Annotated[
    int,
    mapped_column(
        default=lambda: int(time.time()),
        onupdate=lambda: int(time.time()),
    ),
]
