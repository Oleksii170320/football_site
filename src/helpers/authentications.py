from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from fastapi import Request

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_current_user_for_button(request: Request):
    token = request.cookies.get("auth_token")
    return (token, True)


async def get_current_user_for_page(request: Request):
    auth_token = request.cookies.get("auth_token")
    if auth_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невірна аутентифікація",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return auth_token
