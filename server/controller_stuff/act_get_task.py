from .action import Action
from .controller import T

from ..structures import User
from ..tools.status import StatusEnum, Status


class ActionGetTask(Action):
    @staticmethod
    def __get_ready_arg(user: User, transmitter: T, arg: dict, **kwargs) -> Status[dict]:
        user_to_room = kwargs['user_to_room']

        if user not in user_to_room:
            return Status(
                StatusEnum.FAILURE,
                f'user {user.initials()} not in the room',
                data={
                    'action': 'get_task',
                    'status': 'FAILURE',
                    'message': f'user {user.initials()} not in the room',
                    'data': {}
                }
            )

        if user_to_room[user].visitors[user.id].task is not None:
            return Status(
                StatusEnum.REDIRECT,
                'You already have task',
                data={
                    'action': 'get_task',
                    'status': 'REDIRECT',
                    'message': 'You already have task',
                    'data': user_to_room[user].visitors[user.id].task.as_dict()
                }
            )

        return Status(
            StatusEnum.SUCCESS,
            'Ready arg created',
            data={}
        )

    @staticmethod
    def __get_result(user: User, transmitter: T, ready_args: dict, **kwargs) \
            -> Status[list[tuple[dict, T]]] | Status[dict]:
        user_to_room = kwargs['user_to_room']
        user_to_transmitter = kwargs['user_to_transmitter']

        room = user_to_room[user]
        response = room.issue_task(user)

        if response.status != StatusEnum.SUCCESS:
            return Status(
                response.status,
                response.message,
                data={
                    'action': 'get_task',
                    'status': str(response.status),
                    'message': response.message,
                    'data': {}
                }
            )

        data_to_sends: list[tuple[dict, T]] = []

        data_to_sends.append(({
                'action': 'get_task',
                'status': 'SUCCESS',
                'data': {
                    'user': user.as_dict_private()
                }
            },
            user_to_transmitter[room.owner]
        ))

        data_to_sends.append(({
                'action': 'task_issued',
                'status': 'SUCCESS',
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
