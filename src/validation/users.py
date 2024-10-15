# import uuid
# from typing import Optional
#
# from fastapi_users import schemas
#
#
# class UserRead(schemas.BaseUser[int]):
#     id: int
#     email: str
#     username: str
#     role_id: int
#     is_active: Optional[bool] = True
#     is_superuser: Optional[bool] = False
#     is_verified: Optional[bool] = False
#
#     class Config:
#         orm_mode = True
#
#
# class UserCreate(schemas.BaseUserCreate):
#     email: str
#     username: str
#     password_hash: str
#     role_id: int
#     is_active: Optional[bool] = True
#     is_superuser: Optional[bool] = False
#     is_verified: Optional[bool] = False
