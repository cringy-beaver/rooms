from typing import TypeVar, Generic, Hashable
from queue import Queue

import aiohttp as aiohttp

from ..structures import User, Room
from ..tools.status import Status, StatusEnum

from .actions import *

T = TypeVar('T', bound=Hashable)

AUTH_URL = '/user_info'


class Controller(Generic[T]):
    def __init__(self):
        self.user_id_to_room: dict[str, Room] = {}
        self.id_to_room: dict[str, Room] = {}
        self.user_id_to_transmitter: dict[str, T] = {}
        self.rooms: Queue[Room] = Queue()

        self.commands: dict[str, type(Action)] = {
            # ActionChangePosQueue.action_name: ActionChangePosQueue,
            ActionCreateRoom.action_name: ActionCreateRoom,
            ActionGetTask.action_name: ActionGetTask,
            ActionJoinRoom.action_name: ActionJoinRoom,
            ActionJoinQueue.action_name: ActionJoinQueue,
            ActionLeaveQueue.action_name: ActionLeaveQueue,
            ActionNewSubmitting.action_name: ActionNewSubmitting,
            ActionRemoveSubmitting.action_name: ActionRemoveSubmitting,
            ActionLeaveRoom.action_name: ActionLeaveRoom,
        }

    def delete_room(self, room: Room) -> list[tuple[dict, T]]:
        result = []

        data = {
            'action': 'delete_room',
            'status': 'SUCCESS',
            'message': 'Room deleted',
            'data': {}
        }

        for visitor_id in room.id_to_visitor:
            if visitor_id in self.user_id_to_transmitter:
                result.append((data, self.user_id_to_transmitter[visitor_id]))
            del self.user_id_to_room[visitor_id]
            del self.user_id_to_transmitter[visitor_id]

        if room.owner.id in self.user_id_to_transmitter:
            result.append((data, self.user_id_to_transmitter[room.owner.id]))

        del self.user_id_to_room[room.owner.id]
        del self.user_id_to_transmitter[room.owner.id]

        del self.id_to_room[room.id]

        return result

    def delete_old_rooms(self) -> list[tuple[dict, T]]:
        result = []

        for _ in range(self.rooms.qsize()):
            room = self.rooms.queue[0]
            if not room.has_to_be_deleted():
                break

            room = self.rooms.get()
            result.extend(self.delete_room(room))

        return result

    async def get_user_info(self, token: str) -> tuple[Status[User], str]:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                    f'{AUTH_URL}?token={token}'
            ) as resp:
                if resp.status != 200:
                    return Status(
                        StatusEnum.FAILURE,
                        'Bad token'
                    ), token

                data = await resp.json()
                ready_data = {}
                ready_data['name'] = data['user']['name']
                ready_data['second_name'] = data['user']['second_name']
                ready_data['id'] = data['user']['id']
                ready_data['token'] = data['token']

                return Status(
                    StatusEnum.SUCCESS,
                    'Ok',
                    data=User(
                        ready_data['name'],
                        ready_data['second_name'],
                        ready_data['id']
                    )
                ), data['token']

    def get_user_info_test(self, token: str) -> tuple[Status[User], str]:
        if token == '1':
            return Status(
                StatusEnum.SUCCESS,
                'Ok',
                data=User(
                    'Stepan',
                    'Godov',
                    '1234'
                )
            ), '1'
        if token == '2':
            return Status(
                StatusEnum.SUCCESS,
                'Ok',
                data=User(
                    'Arseniy',
                    'Romashov',
                    '1234567'
                )
            ), '2'
        if token == '3':
            return Status(
                StatusEnum.SUCCESS,
                'Ok',
                data=User(
                    'Ivan',
                    'Ivanov',
                    '12345678'
                )
            ), '3'

    async def handle_request(self, data: dict, transmitter: T) -> list[tuple[dict, T]]:
        list_to_send = []

        for _transmitter, data in self.delete_old_rooms():
            list_to_send.append((_transmitter, data))

        action = data['action']
        token = data['token']
        arg = data['data']

        # status, new_token = await self.get_user_info(token)
        status, new_token = self.get_user_info_test(token)

        if status.status == StatusEnum.FAILURE:
            list_to_send.append(
                (
                    {
                        'action': action,
                        'status': 'FAILURE',
                        'message': 'Bad token',
                        'data': {}
                    },
                    transmitter
                )
            )

            return list_to_send

        user = status.data

        response = await self.commands[action].process(
            user,
            transmitter,
            arg,
            user_to_room=self.user_id_to_room,
            id_to_room=self.id_to_room,
            user_to_transmitter=self.user_id_to_transmitter
        )

        for data, _transmitter in response:
            if _transmitter == transmitter:
                data['token'] = new_token
            list_to_send.append((data, _transmitter))

        return list_to_send
