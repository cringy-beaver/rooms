from .action import Action, T

from ...structures import User
from ...tools.status import StatusEnum, Status


class ActionJoinQueue(Action):
    action_name: str = 'join_queue'
    action_message_ok: str = 'User joined'

    @staticmethod
    def get_ready_arg(user: User, transmitter: T, arg: dict, **kwargs) -> Status[dict]:
        id_to_room = kwargs['id_to_room']

        check_status = Action.check_needed_fields(arg, ['room_id'])
        if check_status.status != StatusEnum.SUCCESS:
            return Status(
                StatusEnum.FAILURE,
                check_status.message,
                data={
                    'action': ActionJoinQueue.action_name,
                    'status': str(check_status.status),
                    'message': check_status.message,
                    'data': {}
                }
            )

        if arg['room_id'] not in id_to_room:
            return Status(
                StatusEnum.FAILURE,
                f'Room with id {arg["room_id"]} not found',
                data={
                    'action': ActionJoinQueue.action_name,
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
    def get_result(user: User, transmitter: T, ready_args: dict, **kwargs) \
            -> Status[list[tuple[dict, T]]]:
        id_to_room = kwargs['id_to_room']
        user_id_to_transmitter = kwargs['user_id_to_transmitter']

        room = id_to_room[ready_args['room_id']]

        response = room.get_user_by_id(user.id)

        if response.status != StatusEnum.SUCCESS:
            return Status(
                response.status,
                response.message,
                data=[
                    (
                        {
                            'action': ActionJoinQueue.action_name,
                            'status': str(response.status),
                            'message': response.message,
                            'data': {}
                        },
                        transmitter
                    )
                ]
            )

        _user = response.data

        status = room.join_queue(_user)
        if status.status != StatusEnum.SUCCESS:
            return Status(
                status.status,
                status.message,
                data=[
                    (
                        {
                            'action': ActionJoinQueue.action_name,
                            'status': str(status.status),
                            'message': status.message,
                            'data': {}
                        },
                        transmitter
                    )
                ]
            )

        data_to_sends: list[tuple[dict, T]] = []

        for visitor_id in room.id_to_visitor:
            if room.id_to_visitor[visitor_id] == _user:
                data_to_sends.append((
                    {
                        'action': ActionJoinQueue.action_name,
                        'status': 'SUCCESS',
                        'message': ActionJoinQueue.action_message_ok,
                        'data': {}
                    },
                    transmitter
                ))


            data_to_sends.append((
                {
                    'action': ActionJoinQueue.action_name,
                    'status': 'SUCCESS',
                    'message': ActionJoinQueue.action_message_ok,
                    'data': {
                        'user': _user.as_dict_public(),
                    }
                },
                user_id_to_transmitter[visitor_id]
            ))

        data_to_sends.append((
            {
                'action': ActionJoinQueue.action_name,
                'status': 'SUCCESS',
                'message': ActionJoinQueue.action_message_ok,
                'data': {
                    'user': _user.as_dict_private(),
                }
            },
            user_id_to_transmitter[room.owner.id]
        ))

        return Status(
            StatusEnum.SUCCESS,
            'User joined',
            data=data_to_sends
        )
