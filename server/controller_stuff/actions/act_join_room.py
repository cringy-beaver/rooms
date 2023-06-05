from .action import Action
from ..controller import T

from ...structures import User
from ...tools.status import StatusEnum, Status


class ActionJoinRoom(Action):
    action_name: str = 'join_room'
    action_message_ok: str = 'User joined'

    @staticmethod
    def __get_ready_arg(user: User, transmitter: T, arg: dict, **kwargs) -> Status[dict]:
        user_id_to_room = kwargs['user_id_to_room']
        user_id_to_transmitter = kwargs['user_id_to_transmitter']
        id_to_room = kwargs['id_to_room']

        check_status = Action.check_needed_fields(arg, ['room_id'])
        if check_status.status != StatusEnum.SUCCESS:
            return Status(
                StatusEnum.FAILURE,
                check_status.message,
                data={
                    'action': ActionJoinRoom.action_name,
                    'status': str(check_status.status),
                    'message': check_status.message,
                    'data': {}
                }
            )

        if user.id in user_id_to_room:
            user_id_to_transmitter[user.id] = transmitter
            return Status(
                StatusEnum.REDIRECT,
                'You are already in room',
                data={
                    'action': ActionJoinRoom.action_name,
                    'status': 'REDIRECT',
                    'message': 'You are already in room',
                    'data': user_id_to_room[user].as_dict_by_user(user)
                }
            )

        if arg['room_id'] not in id_to_room:
            return Status(
                StatusEnum.FAILURE,
                f'Room with id {arg["room_id"]} not found',
                data={
                    'action': ActionJoinRoom.action_name,
                    'status': 'FAILURE',
                    'message': f'Room with id {arg["room_id"]} not found',
                    'data': {}
                }
            )

        ready_args = {
            'room_id': arg['room_id']
        }

        return Status(
            StatusEnum.SUCCESS,
            'Ready arg created',
            data=ready_args
        )

    @staticmethod
    def __get_result(user: User, transmitter: T, ready_args: dict, **kwargs) \
            -> Status[list[tuple[dict, T]]]:
        id_to_room = kwargs['id_to_room']
        user_id_to_room = kwargs['user_id_to_room']
        user_id_to_transmitter = kwargs['user_id_to_transmitter']

        room = id_to_room[ready_args['room_id']]

        status = room.join_room(user)
        if status.status != StatusEnum.SUCCESS:
            return Status(
                status.status,
                status.message,
                data=[
                    {
                        'action': ActionJoinRoom.action_name,
                        'status': str(status.status),
                        'message': status.message,
                        'data': {}
                    },
                    transmitter
                ]
            )

        user_id_to_room[user.id] = room
        user_id_to_transmitter[user.id] = transmitter

        data_to_sends: list[tuple[dict, T]] = []

        for visitor_id in room.id_to_visitor:
            if room.id_to_visitor[visitor_id] == user:
                continue

            data_to_sends.append(
                (
                    {
                        'action': ActionJoinRoom.action_name,
                        'status': 'SUCCESS',
                        'message': ActionJoinRoom.action_message_ok,
                        'data': {
                            'user': user.as_dict_public(),
                        }
                    },
                    user_id_to_transmitter[visitor_id]
                )
            )

        data_to_sends.append(
            (
                {
                    'action': ActionJoinRoom.action_name,
                    'status': 'SUCCESS',
                    'message': ActionJoinRoom.action_message_ok,
                    'data': {
                        'user': user.as_dict_private(),
                    }
                },
                user_id_to_transmitter[room.owner.id]
            )
        )

        return Status(
            StatusEnum.SUCCESS,
            'Joined to room',
            data=data_to_sends
        )
