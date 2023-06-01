from typing import TypeVar, Generic, Hashable
import json

from .network_structures import Switchboard
from .structures import User, Task, Room
from .tools.status import Status, StatusEnum


T = TypeVar('T', bound=Hashable)

# TODO:
# 1. Actions:
#     1.1. Create room (✓)
#     1.3. Add user to room (✓)
#     1.4. Remove user from room
#     1.5. Issue task to user (✓)
#     1.6. Get room info for user (✓)
#     1.7. Get room info for owner (✓)
#     1.8. Make user_to_submit task
#         1.8.1 set user_to_submit
#         1.8.2 remove user_to_submit
#     1.9. Join queue
#     1.10. Leave queue
#     1.11. Change position in queue
#     1.12. mix tasks order
#     1.13. parse command

'''
response:
{
    'status': StatusEnum,
    'message': str,
    'data': JSON
}
'''


class Core(Generic[T]):
    def __init__(self, switchboard: Switchboard[T]):
        self.switchboard = switchboard

        self.user_to_room: dict[User, Room] = {}
        self.id_to_room: dict[str, Room] = {}
        self.user_to_transmitter: dict[User, T] = {}

    def __get_room_by_user(self, user: User) -> Status[dict]:
        if user not in self.user_to_room:
            return Status(
                StatusEnum.FAILURE,
                f'user {user.initials()} not in the room'
            )

        return Status(
            StatusEnum.SUCCESS,
            'Room info',
            data=self.user_to_room[user].as_dict_by_user(user)
        )

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









