from abc import ABC, abstractmethod
from typing import TypeVar, Generic

from ...structures import User
from ...tools.status import StatusEnum, Status

T = TypeVar('T')


class Action(Generic[T]):
    action_name: str
    action_message_ok: str

    @staticmethod
    def check_needed_fields(arg: dict, needed_fields: list[str]) -> Status[dict]:
        for key in needed_fields:
            if key not in arg:
                return Status(
                    StatusEnum.FAILURE,
                    f'No {key} field in request'
                )

        return Status(StatusEnum.SUCCESS, 'OK')

    @staticmethod
    def process(act: 'Action', user: User, transmitter: T, arg: dict, **kwargs) \
            -> Status[list[tuple[dict, T]]]:
        ready_arg_status = act.get_ready_arg(user, transmitter, arg, **kwargs)

        if ready_arg_status.status != StatusEnum.SUCCESS:
            return Status(
                ready_arg_status.status,
                ready_arg_status.message,
                data=[
                    (
                        ready_arg_status.data,
                        transmitter
                    )
                ]
            )

        return act.get_result(user, transmitter, ready_arg_status.data, **kwargs)

    @staticmethod
    @abstractmethod
    def get_ready_arg(user: User, transmitter: T, arg: dict, **kwargs) -> Status[dict]:
        pass

    @staticmethod
    @abstractmethod
    def get_result(user: User, transmitter: T, ready_arg: dict, **kwargs) \
            -> Status[list[tuple[dict, T]]]:
        pass
