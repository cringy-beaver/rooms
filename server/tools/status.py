import enum
from typing import TypeVar, Generic

T = TypeVar('T')


class StatusEnum(enum.Enum):
    SUCCESS = 0
    FAILURE = 1
    DENIED = 2


class Status(Generic[T]):
    def __init__(self, status: StatusEnum, message: str, *, data: T = None):
        self.status = status
        self.message = message
        self.data = data
