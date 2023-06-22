from .action import Action, T

from ...structures import User
from ...tools.status import StatusEnum, Status


class ActionGetTask(Action):
    action_name: str = 'get_task'
    action_message_ok: str = 'Task issued'

    @staticmethod
    def get_ready_arg(user: User, transmitter: T, arg: dict, **kwargs) -> Status[dict]:
        user_id_to_room = kwargs['user_id_to_room']

        if user.id not in user_id_to_room:
            return Status(
                StatusEnum.FAILURE,
                f'user {user.initials()} not in the room',
                data={
                    'action': ActionGetTask.action_name,
                    'status': 'FAILURE',
                    'message': f'user {user.initials()} not in the room',
                    'data': {}
                }
            )

        if user_id_to_room[user.id].id_to_visitor[user.id].task is not None:
            return Status(
                StatusEnum.REDIRECT,
                'You already have task',
                data={
                    'action': ActionGetTask.action_name,
                    'status': 'REDIRECT',
                    'message': 'You already have task',
                    'data': {
                        'task': user_id_to_room[user.id].id_to_visitor[user.id].task.as_dict()
                    }
                }
            )

        return Status(
            StatusEnum.SUCCESS,
            'Ready arg created',
            data={}
        )

    @staticmethod
    def get_result(user: User, transmitter: T, ready_args: dict, **kwargs) \
            -> Status[list[tuple[dict, T]]]:
        user_id_to_room = kwargs['user_id_to_room']
        user_id_to_transmitter = kwargs['user_id_to_transmitter']

        response = user_id_to_room[user.id].get_user_by_id(user.id)

        if response.status != StatusEnum.SUCCESS:
            return Status(
                response.status,
                response.message,
                data=[
                    (
                        {
                            'action': ActionGetTask.action_name,
                            'status': str(response.status),
                            'message': response.message,
                            'data': {}
                        },
                        transmitter
                    )
                ]
            )

        _user = response.data

        room = user_id_to_room[_user.id]
        response = room.issue_task(_user)

        if response.status != StatusEnum.SUCCESS:
            return Status(
                response.status,
                response.message,
                data=[
                    (
                        {
                            'action': ActionGetTask.action_name,
                            'status': str(response.status),
                            'message': response.message,
                            'data': {}
                        },
                        transmitter
                    )
                ]
            )

        data_to_sends: list[tuple[dict, T]] = []

        data_to_sends.append((
            {
                'action': ActionGetTask.action_name,
                'status': 'SUCCESS',
                'message': ActionGetTask.action_message_ok,
                'data': {
                    'user': _user.as_dict_private()
                }
            },
            user_id_to_transmitter[room.owner.id]
        ))

        data_to_sends.append((
            {
                'action': ActionGetTask.action_name,
                'status': 'SUCCESS',
                'message': ActionGetTask.action_message_ok,
                'data': {
                    'task': response.data
                }
            },
            transmitter
        ))

        return Status(
            StatusEnum.SUCCESS,
            'Task issued',
            data=data_to_sends
        )
