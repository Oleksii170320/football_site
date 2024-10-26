from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserRead(BaseModel):
    id: int
    username: Optional[str] = None
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool
    is_superuser: bool
    created_at: datetime

    class Config:
        orm_mode = True


class UserCreate(BaseModel):
    username: Optional[str] = None
    email: EmailStr
    password: str  # Пароль передається у відкритому вигляді для хешування
    full_name: Optional[str] = None


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None
