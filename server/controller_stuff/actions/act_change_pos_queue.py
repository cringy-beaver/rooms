# from .action import Action
# from ..controller import T
#
# from ...structures import User
# from ...tools.status import StatusEnum, Status
#
# '''
# Пока не реализовано
# '''
#
# class ActionChangePosQueue(Action):
#     action_name: str = 'change_pos_queue'
#     action_message_ok: str = 'User changed position'
#
#     @staticmethod
#     def __get_ready_arg(user: User, transmitter: T, arg: dict, **kwargs) -> Status[dict]:
#         id_to_room = kwargs['id_to_room']
#
#         check_status = Action.check_needed_fields(arg, ['room_id', 'pos_1', 'pos_2'])
#         if check_status.status != StatusEnum.SUCCESS:
#             return Status(
#                 StatusEnum.FAILURE,
#                 check_status.message,
#                 data={
#                     'action': ActionChangePosQueue.action_name,
#                     'status': str(check_status.status),
#                     'message': check_status.message,
#                     'data': {}
#                 }
#             )
#
#         if arg['room_id'] not in id_to_room:
#             return Status(
#                 StatusEnum.FAILURE,
#                 f'Room with id {arg["room_id"]} not found',
#                 data={
#                     'action': ActionChangePosQueue.action_name,
#                     'status': 'FAILURE',
#                     'message': f'Room with id {arg["room_id"]} not found',
#                     'data': {}
#                 }
#             )
#
#         ready_args = {
#             'room_id': arg['room_id'],
#             'pos_1': arg['pos_1'],
#             'pos_2': arg['pos_2']
#         }
#
#         return Status(
#             StatusEnum.SUCCESS,
#             'Ready arg created',
#             data=ready_args
#         )
#
#     @staticmethod
#     def __get_result(user: User, transmitter: T, ready_args: dict, **kwargs) \
#             -> Status[list[tuple[dict, T]]] | Status[dict]:
#         id_to_room = kwargs['id_to_room']
#         user_id_to_transmitter = kwargs['user_id_to_transmitter']
#
#         room = id_to_room[ready_args['room_id']]
#         pos_1 = ready_args['pos_1']
#         pos_2 = ready_args['pos_2']
#
#         status = room.change_position_queue(user, pos_1, pos_2)
#         if status.status != StatusEnum.SUCCESS:
#             return Status(
#                 status.status,
#                 status.message,
#                 data={
#                     'action': ActionChangePosQueue.action_name,
#                     'status': str(status.status),
#                     'message': status.message,
#                     'data': {}
#                 }
#             )
#
#         data_to_sends: list[tuple[dict, T]] = []
#
#         for visitor_id in room.id_to_visitor:
#             if room.id_to_visitor[visitor_id] == user:
#                 continue
#
#             data_to_sends.append(
#                 (
#                     {
#                         'action': ActionChangePosQueue.action_name,
#                         'status': 'SUCCESS',
#                         'message': ActionChangePosQueue.action_message_ok,
#                         'data': {
#                             'user': user.as_dict_public(),
#                             'pos_1': pos_1,
#                             'pos_2': pos_2
#                         }
#                     },
#                     user_id_to_transmitter[visitor_id]
#                 )
#             )
#
#         data_to_sends.append(
#             (
#                 {
#                     'action': ActionChangePosQueue.action_name,
#                     'status': 'SUCCESS',
#                     'message': ActionChangePosQueue.action_message_ok,
#                     'data': {
#                         'user': user.as_dict_private(),
#                         'pos_1': pos_1,
#                         'pos_2': pos_2
#                     }
#                 },
#                 user_id_to_transmitter[room.owner.id]
#             )
#         )
#
#         return Status(
#             StatusEnum.SUCCESS,
#             ActionChangePosQueue.action_message_ok,
#             data=data_to_sends
#         )
