from .action import Action
from .controller import T

from ..structures import User
from ..tools.status import StatusEnum, Status


class ActionNewSubmitting(Action):
    @staticmethod
    def __get_ready_arg(user: User, transmitter: T, arg: dict, **kwargs) -> Status[dict]:
        check_status = Action.check_needed_fields(arg, ['room_id'])
        if check_status.status != StatusEnum.SUCCESS:
            return check_status

        return Status(
            StatusEnum.SUCCESS,
            'Ready arg created',
            data={
                'room_id': arg['room_id']
            }
        )

    @staticmethod
    def __get_result(user: User, transmitter: T, ready_args: dict, **kwargs) \
            -> Status[list[tuple[dict, T]]] | Status[dict]:
        id_to_room = kwargs['id_to_room']
        room = id_to_room[ready_args['room_id']]
        user_to_transmitter = kwargs['user_to_transmitter']

        if user.id not in room.visitors:
            return Status(
                StatusEnum.FAILURE,
                'User is not in this room'
            )

        response = room.new_submitting(user)

        if response.status != StatusEnum.SUCCESS:
            return response

        submitting = response.data
        data_to_send = []

        for visitor_id in room.visitors:
            data_to_send.append((
                {
                    'action': 'new_submitting',
                    'data' : {
                        'user': submitting.as_dict_public()
                    }
                },
                user_to_transmitter[room.visitors[visitor_id]]
            ))

        data_to_send.append((
            {
                'action': 'new_submitting',
                'data': {
                        'user': submitting.as_dict_private()
                    }
            },
            transmitter
        ))

        return Status(
            StatusEnum.SUCCESS,
            'Submitting created',
            data=data_to_send
        )
