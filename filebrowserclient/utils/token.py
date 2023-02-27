import base64
import json
from time import time

from filebrowserclient.models import User


class Token:
    _user = None

    def __init__(self, token):
        self.raw = token
        self.header, self.body = self.decode(self.raw)

    @staticmethod
    def decode(token):
        header, body, *_ = token.split(".")
        return (
            json.loads(base64.b64decode(header + '==')),
            json.loads(base64.b64decode(body + '==')),
        )

    @property
    def exp(self) -> int:
        return self.body["exp"]

    @property
    def iat(self) -> int:
        return self.body["iat"]

    @property
    def user(self) -> User:
        if not self._user:
            self._user = User.parse_obj(self.body["user"])
        return self._user

    @property
    def expired(self) -> bool:
        return time() > self.exp

    def __str__(self):
        return self.raw

