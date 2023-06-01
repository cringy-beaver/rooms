from abc import ABC, abstractmethod
from typing import TypeVar, Generic

from ..tools.status import Status

T = TypeVar('T')


class Switchboard(ABC, Generic[T]):
    @abstractmethod
    async def send(self, data: str, transmitter: T) -> Status:
        pass

    @abstractmethod
    async def receive(self, transmitter: T) -> Status[str]:
        pass

    @abstractmethod
    async def send_and_receive(self, data: str, transmitter: T) -> Status[str]:
        pass

    @abstractmethod
    def close(self, transmitter: T) -> Status:
        pass
