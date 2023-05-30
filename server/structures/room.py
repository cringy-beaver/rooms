from .user import User
from .task import Task

from hashlib import sha256

from ..tools.status import Status, StatusEnum

MAX_VISITORS = 50


class Room:
    def __init__(self, owner: User, tasks: list[Task],
                 max_visitors: int = MAX_VISITORS, description: str = ''):
        self.owner = owner
        self.tasks = tasks
        self.max_visitors = max_visitors
        self.description = description

        self.tasks_order: list[int] = list(range(len(tasks)))
        self.visitors: set[User] = set()

        self.queue: list[User] = []

        self.id: str = self.__generate_id()

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return self.id == other.id

    def __generate_id(self) -> str:
        return sha256(self.owner.id.encode()).hexdigest()

    def join(self, user: User) -> Status[dict]:
        if user in self.visitors:
            return Status(
                StatusEnum.SUCCESS,
                f"User '{user.name} {user.second_name}' already in room",
                data=self.as_dict_by_user(user)
            )

        if len(self.visitors) >= self.max_visitors:
            return Status(
                StatusEnum.FAILURE,
                f"Room is full"
            )

        self.visitors.add(user)

        return Status(
            StatusEnum.SUCCESS,
            f"User '{user.name} {user.second_name}' joined",
            data=self.as_dict_by_user(user)
        )

    def join_to_queue(self, req_user: User) -> Status[None]:
        if req_user == self.owner:
            return Status(
                StatusEnum.DENIED,
                f"Owner can't join to queue"
            )

        if req_user in self.queue:
            return Status(
                StatusEnum.SUCCESS,
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
            f"User '{task.name}' poped from queue"
        )

    def change_position_queue(self, req_user: User, index_1: int, index_2: int) -> Status[tuple[int, int]]:
        if req_user != self.owner:
            return Status(
                StatusEnum.DENIED,
                f"Only owner can change position in queue"
            )

        if index_1 < 0 or index_1 >= len(self.queue) or index_2 < 0 or index_2 >= len(self.queue):
            return Status(
                StatusEnum.FAILURE,
                f"Index out of range"
            )

        self.queue[index_1], self.queue[index_2] = self.queue[index_2], self.queue[index_1]

        return Status(
            StatusEnum.SUCCESS,
            f"Positions changed",
            data=(index_1, index_2)
        )

    def as_dict_by_user(self, user: User) -> dict:
        if user == self.owner:
            return self.__as_dict_private()

        return self.__as_dict_public()

    def __as_dict_public(self) -> dict:
        ...

    def __as_dict_private(self) -> dict:
        ...
