from typing import TypeVar, Generic, Hashable
import json

from .network_structures import Switchboard
from .structures import User, Task, Room
from .tools.status import Status, StatusEnum

from .action import Action
from .act_create_room import ActionCreateRoom


T = TypeVar('T', bound=Hashable)


'''
response:
{
    'status': StatusEnum,
    'message': str,
    'data': JSON
}
'''


class Controller(Generic[T]):
    def __init__(self, switchboard: Switchboard[T]):
        self.switchboard = switchboard

        self.user_to_room: dict[User, Room] = {}
        self.id_to_room: dict[str, Room] = {}
        self.user_to_transmitter: dict[User, T] = {}

        self.commands: dict[str, type(Action)] = {
            'create_room': ActionCreateRoom
        }


    async def handle_request(self, req: str, transmitter: T) -> Status[json]:
        try:
            data = json.loads(req)
        except json.JSONDecodeError:
            return Status(
                StatusEnum.FAILURE,
                'Bad json'
            )

        token = ...
        action = ...
        arg = ...

        user_info = ...

        user = ...

        response = await self.commands[action].process(
            user,
            transmitter,
            arg,
            user_to_room=self.user_to_room,
            id_to_room=self.id_to_room,
            user_to_transmitter=self.user_to_transmitter
        )

        return Status(
            response.status,
            response.message,
            data=response.data
        )










