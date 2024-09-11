import json

from fastapi import Request, Response
from cryptography.fernet import Fernet


key = b"uytbnTTvQmYVZv-mGthawHP-YoFb0btAdH6B7CVcK8M="
f = Fernet(key)


class Session:
    def __init__(self, response: Response):
        self.response = response
        self.data = {}
        if token := response.cookies.get("sessionKey"):
            return self.data.update(json.loads(f.decrypt(token.encode())))

    def __setitem__(self, key, value):
        self.data[key] = value
        token = f.encrypt(json.dumps(self.data).encode()).decode()
        self.response.set_cookie("sessionKey", token)

    def __getitem__(self, key):
        return self.data.get(key)

    def get(self, key: str):
        return self.data.get(key)


def get_session(response: Response):
    return Session(response)
