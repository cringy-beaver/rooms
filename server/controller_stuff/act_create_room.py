from .action import Action
from .controller import T

from ..structures import User, Task, Room
from ..tools.status import StatusEnum, Status


class ActionCreateRoom(Action):
    @staticmethod
    def __get_ready_arg(user: User, transmitter: T, arg: dict, **kwargs) -> Status[dict]:
        user_to_room = kwargs['user_to_room']

        check_status = Action.check_needed_fields(arg, ['tasks'])
        if check_status.status != StatusEnum.SUCCESS:
            return Status(
                StatusEnum.FAILURE,
                check_status.message,
                data={
                    'action': 'create_room',
                    'status': 'FAILURE',
                    'message': check_status.message,
                    'data': {}
                }
            )

        if user in user_to_room:
            return Status(
                StatusEnum.REDIRECT,
                'You are already in room',
                data={
                    'action': 'create_room',
                    'status': 'REDIRECT',
                    'message': 'You are already in room',
                    'data': user_to_room[user].as_dict_by_user(user)
                }
            )

        tasks = []
        for task_dict in arg['tasks']:
            task = Task.from_dict(task_dict)
            if task.status != StatusEnum.SUCCESS:
                return Status(
                    StatusEnum.FAILURE,
                    f'Invalid task: {task.message}',
                    data={
                        'action': 'create_room',
                        'status': 'FAILURE',
                        'message': f'Invalid task: {task.message}',
                        'data': {}
                    }
                )

            tasks.append(task.data)

        ready_args = {
            'owner': user,
            'tasks': tasks
        }

        if 'max_visitors' in arg:
            if not isinstance(arg['max_visitors'], int):
                return Status(
                    StatusEnum.FAILURE,
                    'max_visitors must be int',
                    data={
                        'action': 'create_room',
                        'status': 'FAILURE',
                        'message': 'max_visitors must be int',
                        'data': {}
                    }
                )
            ready_args['max_visitors'] = arg['max_visitors']

        if 'description' in arg:
            ready_args['description'] = arg['description']

        return Status(
            StatusEnum.SUCCESS,
            'Ready arg created',
            data=ready_args
        )

    @staticmethod
    def __get_result(user: User, transmitter: T, ready_args: dict, **kwargs) \
            -> Status[list[tuple[dict, T]]] | Status[dict]:
        user_to_room = kwargs['user_to_room']
        user_to_transmitter = kwargs['user_to_transmitter']
        id_to_room = kwargs['id_to_room']

        room = Room(**ready_args)
        user_to_room[user] = room
        user_to_transmitter[user] = transmitter
        id_to_room[room.id] = room

        return Status(
            StatusEnum.SUCCESS,
            'Room created',
            data=[
                ({
                    'action': 'create_room',
                    'status': 'SUCCESS',
                    'message': 'Room created',
                    'data': room.as_dict_by_user(user)
                 },
                 transmitter)
            ]
        )


