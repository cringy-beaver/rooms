from .action import Action
from ..controller import T

from ...structures import User
from ...tools.status import StatusEnum, Status


class ActionGetRoomInfo(Action):
    action_name: str = 'get_room_info'
    action_message_ok: str = 'Room info'

    @staticmethod
    def __get_ready_arg(user: User, transmitter: T, arg: dict, **kwargs) -> Status[dict]:
        check_status = Action.check_needed_fields(arg, ['room_id'])
        if check_status.status != StatusEnum.SUCCESS:
            return Status(
                StatusEnum.FAILURE,
                'Not enough fields',
                data={
                    'action': ActionGetRoomInfo.action_name,
                    'status': str(check_status.status),
                    'message': check_status.message,
                    'data': {}
                }
            )

        return Status(
            StatusEnum.SUCCESS,
            'Ready arg created',
            data={
                'room_id': arg['room_id']
            }
        )

    @staticmethod
    def __get_result(user: User, transmitter: T, ready_args: dict, **kwargs) \
            -> Status[list[tuple[dict, T]]]:
        id_to_room = kwargs['id_to_room']
        room = id_to_room[ready_args['room_id']]

        return Status(
            StatusEnum.SUCCESS,
            'Room info',
            data=[
                ({
                     'action': ActionGetRoomInfo.action_name,
                     'status': 'SUCCESS',
                     'message': ActionGetRoomInfo.action_message_ok,
                     'data': room.as_dict_by_user(user)
                 }, transmitter)
            ]
        )
