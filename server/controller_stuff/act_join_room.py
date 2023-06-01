from .action import Action
from .controller import T

from ..structures import User
from ..tools.status import StatusEnum, Status


class ActionJoinRoom(Action):
    @staticmethod
    def __get_ready_arg(user: User, transmitter: T, arg: dict, **kwargs) -> Status[dict]:
        user_to_room = kwargs['user_to_room']
        id_to_room = kwargs['id_to_room']

        check_status = Action.check_needed_fields(arg, ['room_id'])
        if check_status.status != StatusEnum.SUCCESS:
            return check_status

        if user in user_to_room:
            return Status(
                StatusEnum.REDIRECT,
                'You are already in room',
                data=user_to_room[user].as_dict_by_user(user)
            )

        if arg['room_id'] not in id_to_room:
            return Status(
                StatusEnum.FAILURE,
                f'Room with id {arg["room_id"]} not found'
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
            -> Status[list[tuple[dict, T]]] | Status[dict]:
        id_to_room = kwargs['id_to_room']
        user_to_room = kwargs['user_to_room']
        user_to_transmitter = kwargs['user_to_transmitter']

        room = id_to_room[ready_args['room_id']]

        status = room.join(user)
        if status.status != StatusEnum.SUCCESS:
            return status

        user_to_room[user] = room
        user_to_transmitter[user] = transmitter

        data_to_sends: list[tuple[dict, T]] = []

        for visitor_id in room.visitors:
            if room.visitors[visitor_id] == user:
                continue

            data_to_sends.append(
                (
                    {
                        'action': 'user_joined',
                        'data': {
                            'user': user.as_dict_public(),
                        }
                    },
                    user_to_transmitter[room.visitors[visitor_id]]
                )
            )

        data_to_sends.append(
            (
                {
                    'action': 'user_joined',
                    'data': {
                        'user': user.as_dict_private(),
                    }
                },
                user_to_transmitter[room.owner]
            )
        )

        return Status(
            StatusEnum.SUCCESS,
            'Joined to room',
            data=data_to_sends
        )
