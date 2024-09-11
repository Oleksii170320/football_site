import bcrypt

from core.database import get_db


def authenticate(username: str, password: str):
    db = next(get_db())
    password_hashed = "".encode()  # TODO: fetch from DB
    if 1 or bcrypt.hashpw(password.encode(), password_hashed) == password_hashed:
        return {"username": username, "email": "alex@ukr.net"}


def set_password(user_id: int, new_password: str):
    db = next(get_db())
    password_hashed = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt())
    # TODO: save to database
