from datetime import datetime

from .user import User
from .task import Task

from hashlib import sha256
from random import shuffle

from ..tools.status import Status, StatusEnum

MAX_VISITORS = 50
TTL = 60 * 60 * 3


class Room:
    def __init__(self, owner: User, tasks: list[Task],
                 max_visitors: int = MAX_VISITORS, description: str = ''):
        self.owner = owner
        self.tasks = tasks
        self.max_visitors = max_visitors
        self.description = description

        self.task_to_take_index: int = 0
        self.tasks_order: list[int] = list(range(len(tasks)))
        self.id_to_visitor: dict[str, User] = {}

        self.time_created: datetime = datetime.now()
        self.ttl = TTL

        self.submitting_user: User | None = None
        self.queue: list[User] = []

        self.id: str = self.__generate_id()
        self.__reset_order()

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return self.id == other.id

    def has_to_be_deleted(self) -> bool:
        return (datetime.now() - self.time_created).seconds > self.ttl

    def __generate_id(self) -> str:
        return sha256(self.owner.id.encode()).hexdigest()

    def __reset_order(self) -> None:
        shuffle(self.tasks_order)
        self.task_to_take_index = 0

    def get_user_by_id(self, user_id: str) -> Status[User]:
        if user_id == self.owner.id:
            return Status(
                StatusEnum.SUCCESS,
                "User found",
                data=self.owner
            )

        if user_id in self.id_to_visitor:
            return Status(
                StatusEnum.SUCCESS,
                "User found",
                data=self.id_to_visitor[user_id]
            )

        return Status(
            StatusEnum.FAILURE,
            "User not found"
        )

    def new_submitting(self, user: User) -> Status[User]:
        if user != self.owner:
            return Status(
                StatusEnum.DENIED,
                f"Only owner can delete submitting user"
            )

        if len(self.queue) == 0:
            self.submitting_user = None
            return Status(
                StatusEnum.FAILURE,
                f"Queue is empty"
            )

        self.submitting_user = self.queue.pop(0)

        return Status(
            StatusEnum.SUCCESS,
            "Submitting user updated",
            data=self.submitting_user
        )

    def remove_submitting(self, user: User) -> Status[None]:
        if user != self.owner:
            return Status(
                StatusEnum.DENIED,
                f"Only owner can delete submitting user"
            )

        self.submitting_user = None

        return Status(
            StatusEnum.SUCCESS,
            f"Submitting user deleted"
        )

    def issue_task(self, user: User) -> Status[dict]:
        if user.task is not None:
            return Status(
                StatusEnum.DENIED,
                f"User '{user.name} {user.second_name}' already has task"
            )

        if user == self.owner:
            return Status(
                StatusEnum.DENIED,
                f"Owner can't take task"
            )

        if user.id not in self.id_to_visitor:
            return Status(
                StatusEnum.DENIED,
                f"User '{user.name} {user.second_name}' not in room"
            )

        if self.task_to_take_index >= len(self.tasks_order):
            self.__reset_order()

        task = self.tasks[self.tasks_order[self.task_to_take_index]]
        self.task_to_take_index += 1
        user.set_task(task)

        return Status(
            StatusEnum.SUCCESS,
            f"User '{user.name} {user.second_name}' took task",
            data=task.as_dict()
        )

    def join_room(self, user: User) -> Status[dict]:
        if user.id in self.id_to_visitor:
            return Status(
                StatusEnum.SUCCESS,
                f"User '{user.name} {user.second_name}' already in room",
                data=self.as_dict_by_user(user)
            )

        if len(self.id_to_visitor) >= self.max_visitors:
            return Status(
                StatusEnum.FAILURE,
                f"Room is full"
            )

        self.id_to_visitor[user.id] = user

        return Status(
            StatusEnum.SUCCESS,
            f"User '{user.name} {user.second_name}' joined",
            data=self.as_dict_by_user(user)
        )

    def leave_room(self, user: User, user_id: str) -> Status[list[User]]:
        if user != self.owner and user.id != user_id:
            return Status(
                StatusEnum.DENIED,
                f"Only owner can delete submitting user"
            )

        _user = self.id_to_visitor[user_id]

        if _user == self.owner:
            return Status(
                StatusEnum.SUCCESS_EXIT,
                'Success, send visitors that room will be deleted',
                data=list(self.id_to_visitor.values())
            )

        if _user.id not in self.id_to_visitor:
            return Status(
                StatusEnum.FAILURE,
                f"User '{_user.name} {_user.second_name}' not in room"
            )

        self.id_to_visitor.pop(_user.id)

        return Status(
            StatusEnum.SUCCESS,
            f"User '{_user.name} {_user.second_name}' left",
            data=[]
        )

    def join_queue(self, req_user: User) -> Status[None]:
        if req_user == self.owner:
            return Status(
                StatusEnum.DENIED,
                f"Owner can't join to queue"
            )

        if req_user.id not in self.id_to_visitor:
            return Status(
                StatusEnum.DENIED,
                f"User '{req_user.name} {req_user.second_name}' not in room"
            )

        if req_user in self.queue:
            return Status(
                StatusEnum.REDIRECT,
                f"User '{req_user.name} {req_user.second_name}' already in queue"
            )

        self.queue.append(req_user)

        return Status(
            StatusEnum.SUCCESS,
            f"User '{req_user.name} {req_user.second_name}' joined to queue"
        )

    def pop_from_queue(self, req_user: User, index: int = 0) -> Status[None]:
        if len(self.queue) == 0:
            return Status(
                StatusEnum.FAILURE,
                f"Queue is empty"
            )

        if req_user != self.owner:
            index = self.queue.index(req_user)
            if index == -1:
                return Status(
                    StatusEnum.FAILURE,
                    f"User '{req_user.name} {req_user.second_name}' not in queue"
                )

        task = self.queue.pop(index)

        return Status(
            StatusEnum.SUCCESS,
            f"User '{task.name}' popped from queue"
        )

    # def change_position_queue(self, req_user: User, index_1: int, index_2: int) -> Status[tuple[int, int]]:
    #     if req_user != self.owner:
    #         return Status(
    #             StatusEnum.DENIED,
    #             f"Only owner can change position in queue"
    #         )
    #
    #     if index_1 < 0 or index_1 >= len(self.queue) or index_2 < 0 or index_2 >= len(self.queue):
    #         return Status(
    #             StatusEnum.FAILURE,
    #             f"Index out of range"
    #         )
    #
    #     self.queue[index_1], self.queue[index_2] = self.queue[index_2], self.queue[index_1]
    #
    #     return Status(
    #         StatusEnum.SUCCESS,
    #         f"Positions changed",
    #         data=(index_1, index_2)
    #     )

    def as_dict_by_user(self, user: User) -> dict:
        if user == self.owner:
            return self.__as_dict_private()

        return self.__as_dict_public()

    def __as_dict_public(self) -> dict:
        return {
            'owner': self.owner.as_dict_public(),
            'queue': [user.as_dict_public() for user in self.queue],
            'submitting_user': self.submitting_user.as_dict_public() if self.submitting_user is not None else None,
            'users_not_in_queue': [user.as_dict_public() for user in self.id_to_visitor.values() if user not in self.queue],
            'id': self.id,
        }

    def __as_dict_private(self) -> dict:
        return {
            'owner': self.owner.as_dict_private(),
            'queue': [user.as_dict_private() for user in self.queue],
            'submitting_user': self.submitting_user.as_dict_private() if self.submitting_user is not None else None,
            'users_not_in_queue': [user.as_dict_private() for user in self.id_to_visitor.values() if user not in self.queue],
            'id': self.id,
        }
