import enum
import json
from typing import TypeVar, Generic

T = TypeVar('T')


class StatusEnum(enum.Enum):
    SUCCESS = 0
    FAILURE = 1
    DENIED = 2
    SUCCESS_EXIT = 3
    REDIRECT = 4
    SECOND_ACTION = 5
    UNKNOWN = 6
    UPDATE = 7

    def __str__(self):
        return self.name


class Status(Generic[T]):
    def __init__(self, status: StatusEnum, message: str, *, data: T = None):
        self.status = status
        self.message = message
        self.data = data

    def as_json(self) -> json:
        return json.dumps({
            'status': str(self.status),
            'message': self.message,
            'data': self.data
        })
