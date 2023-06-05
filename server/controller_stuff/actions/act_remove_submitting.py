from .action import Action
from ..controller import T

from ...structures import User
from ...tools.status import StatusEnum, Status


class ActionRemoveSubmitting(Action):
    action_name: str = 'remove_submitting'
    action_message_ok: str = 'Submitting removed'

    @staticmethod
    def __get_ready_arg(user: User, transmitter: T, arg: dict, **kwargs) -> Status[dict]:
        check_status = Action.check_needed_fields(arg, ['room_id'])
        if check_status.status != StatusEnum.SUCCESS:
            return Status(
                check_status.status,
                check_status.message,
                data={
                    'action': ActionRemoveSubmitting.action_name,
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
        user_id_to_transmitter = kwargs['user_id_to_transmitter']

        response = room.get_user_by_id(user.id)
        if response.status != StatusEnum.SUCCESS:
            return Status(
                response.status,
                response.message,
                data=[
                    {
                        'action': ActionRemoveSubmitting.action_name,
                        'status': str(response.status),
                        'message': response.message,
                        'data': {}
                    },
                    transmitter
                ]
            )

        _user = response.data

        response = room.remove_submitting(_user)

        if response.status != StatusEnum.SUCCESS:
            return Status(
                response.status,
                response.message,
                data=[
                    {
                        'action': ActionRemoveSubmitting.action_name,
                        'status': 'FAILURE',
                        'message': response.message,
                        'data': {}
                    },
                    transmitter
                ]
            )

        data_to_send = []

        for visitor_id in room.id_to_visitor:
            data_to_send.append((
                {
                    'action': ActionRemoveSubmitting.action_name,
                    'status': 'SUCCESS',
                    'message': ActionRemoveSubmitting.action_message_ok,
                    'data': {
                    }
                },
                user_id_to_transmitter[visitor_id]
            ))

        data_to_send.append((
            {
                'action': ActionRemoveSubmitting.action_name,
                'status': 'SUCCESS',
                'message': ActionRemoveSubmitting.action_message_ok,
                'data': {
                }
            },
            transmitter
        ))

        return Status(
            StatusEnum.SUCCESS,
            'Submitting created',
            data=data_to_send
        )
