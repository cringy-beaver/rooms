from .action import Action, T

from ...structures import User
from ...tools.status import StatusEnum, Status


class ActionLeaveRoom(Action):
    action_name: str = 'leave_room'
    action_secondary_name: str = 'close_room'
    action_message_ok: str = 'User left'
    action_message_ok_secondary: str = 'Room closed'

    @staticmethod
    def get_ready_arg(user: User, transmitter: T, arg: dict, **kwargs) -> Status[dict]:
        user_id_to_room = kwargs['user_id_to_room']
        id_to_room = kwargs['id_to_room']

        check_status = Action.check_needed_fields(arg, ['room_id', 'user_id'])
        if check_status.status != StatusEnum.SUCCESS:
            return Status(
                StatusEnum.FAILURE,
                check_status.message,
                data={
                    'action': ActionLeaveRoom.action_name,
                    'status': str(check_status.status),
                    'message': check_status.message,
                    'data': {}
                }
            )

        if user.id not in user_id_to_room:
            return Status(
                StatusEnum.FAILURE,
                'You are not in room',
                data={
                    'action': ActionLeaveRoom.action_name,
                    'status': 'FAILURE',
                    'message': 'You are not in room',
                    'data': {}
                }
            )

        if arg['room_id'] not in id_to_room:
            return Status(
                StatusEnum.FAILURE,
                f'Room with id {arg["room_id"]} not found',
                data={
                    'action': ActionLeaveRoom.action_name,
                    'status': 'FAILURE',
                    'message': f'Room with id {arg["room_id"]} not found',
                    'data': {}
                }
            )

        ready_args = {
            'room_id': arg['room_id'],
            'user_id': arg['user_id']
        }

        return Status(
            StatusEnum.SUCCESS,
            'Ready arg created',
            data=ready_args
        )

    @staticmethod
    def get_result(visitor_id: User, transmitter: T, ready_args: dict, **kwargs) \
            -> Status[list[tuple[dict, T]]]:
        id_to_room = kwargs['id_to_room']
        user_id_to_room = kwargs['user_id_to_room']
        user_id_to_transmitter = kwargs['user_id_to_transmitter']

        room = id_to_room[ready_args['room_id']]
        user_to_pop_id = ready_args['user_id']

        response = room.get_user_by_id(visitor_id.id)
        if response.status != StatusEnum.SUCCESS:
            return Status(
                response.status,
                response.message,
                data=[
                    (
                        {
                            'action': ActionLeaveRoom.action_name,
                            'status': str(response.status),
                            'message': response.message,
                            'data': {}
                        },
                        transmitter
                    )
                ]
            )

        _user = response.data

        status = room.leave_room(_user, user_to_pop_id)

        if status.status not in [StatusEnum.SUCCESS, StatusEnum.SUCCESS_EXIT]:
            return Status(
                status.status,
                status.message,
                data=[
                    (
                        {
                            'action': ActionLeaveRoom.action_name,
                            'status': str(status.status),
                            'message': status.message,
                            'data': {}
                        },
                        transmitter
                    )
                ]
            )

        if status.status == StatusEnum.SUCCESS_EXIT:
            data_to_sends: list[tuple[dict, T]] = []
            visitors = status.data

            for visitor_id in visitors:
                data_to_sends.append(
                    (
                        {
                            'action': ActionLeaveRoom.action_secondary_name,
                            'status': 'SUCCESS',
                            'message': ActionLeaveRoom.action_message_ok_secondary,
                            'target': 'visitor',
                            'data': {}
                        },
                        user_id_to_transmitter[visitor_id.id]
                    )
                )

                del user_id_to_room[visitor_id.id]
                del user_id_to_transmitter[visitor_id.id]

            data_to_sends.append(
                (
                    {
                        'action': ActionLeaveRoom.action_secondary_name,
                        'status': 'SUCCESS',
                        'message': ActionLeaveRoom.action_message_ok_secondary,
                        'target': 'owner',
                        'data': {}
                    },
                    user_id_to_transmitter[room.owner.id]
                )
            )

            del user_id_to_room[room.owner.id]
            del user_id_to_transmitter[room.owner.id]
            del id_to_room[room.id]

            return Status(
                StatusEnum.SUCCESS,
                'Room closed',
                data=data_to_sends
            )

        data_to_sends: list[tuple[dict, T]] = []
        user_left = status.data[0]

        for visitor_id in room.id_to_visitor:
            data_to_sends.append(
                (
                    {
                        'action': ActionLeaveRoom.action_name,
                        'status': 'SUCCESS',
                        'message': ActionLeaveRoom.action_message_ok,
                        'data': {
                            'user': user_left.as_dict_public()
                        }
                    },
                    user_id_to_transmitter[visitor_id]
                )
            )

        data_to_sends.append(
            (
                {
                    'action': ActionLeaveRoom.action_name,
                    'status': 'SUCCESS',
                    'message': ActionLeaveRoom.action_message_ok,
                    'data': {
                        'user': user_left.as_dict_private()
                    }
                },

                user_id_to_transmitter[user_left.id]
            )
        )

        data_to_sends.append(
            (
                {
                    'action': ActionLeaveRoom.action_name,
                    'status': 'SUCCESS',
                    'message': ActionLeaveRoom.action_message_ok,
                    'data': {
                        'user': user_left.as_dict_private()
                    }
                },
                user_id_to_transmitter[room.owner.id]
            )
        )

        del user_id_to_room[user_left.id]
        del user_id_to_transmitter[user_left.id]

        return Status(
            StatusEnum.SUCCESS,
            'User left',
            data=data_to_sends
        )
