from .user import User
from .task import Task

from hashlib import sha256
from random import shuffle

from ..tools.status import Status, StatusEnum

MAX_VISITORS = 50

'''
TODO: 
1. Actions:
    1.1. Create room (✓)
    1.3. Add user to room (✓)
    1.4. Remove user from room
    1.5. Issue task to user (✓)
    1.6. Get room info for user (✓)
    1.7. Get room info for owner (✓)
    1.8. Make user_to_submit task (✓)
        1.8.1 set user_to_submit (✓)
        1.8.2 remove user_to_submit (✓)
    1.9. Join queue (✓)
    1.10. Leave queue (✓)
    1.11. Change position in queue (✓)
    1.12. mix tasks order (✓)
2. fields:
    2.1. owner (✓)
    2.2. tasks (✓)
    2.3. max_visitors (✓)
    2.4. description (✓)
    2.5. task_to_take_index (✓)
    2.6. tasks_order (✓)
    2.7. visitors (✓)
    2.8. queue (✓)
    2.9. id (✓)
3. methods:
    3.1. __init__ (✓)
    3.2. __hash__ (✓)
    3.3. __eq__ (✓)
    3.4. __generate_id (✓)
    3.5. __reset_order (✓)
    3.6. from_dict    
'''


class Room:
    def __init__(self, owner: User, tasks: list[Task],
                 max_visitors: int = MAX_VISITORS, description: str = ''):
        self.owner = owner
        self.tasks = tasks
        self.max_visitors = max_visitors
        self.description = description

        self.task_to_take_index: int = 0
        self.tasks_order: list[int] = list(range(len(tasks)))
        self.visitors: dict[str, User] = {
            owner.id: owner
        }

        self.submitting_user: User | None = None
        self.queue: list[User] = []

        self.id: str = self.__generate_id()

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return self.id == other.id

    def __generate_id(self) -> str:
        return sha256(self.owner.id.encode()).hexdigest()

    def __reset_order(self) -> None:
        shuffle(self.tasks_order)
        self.task_to_take_index = 0

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

        if user.id not in self.visitors:
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

    def join(self, user: User) -> Status[dict]:
        if user.id in self.visitors:
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

        self.visitors[user.id] = user

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

        if req_user.id not in self.visitors:
            return Status(
                StatusEnum.DENIED,
                f"User '{req_user.name} {req_user.second_name}' not in room"
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
            f"User '{task.name}' popped from queue"
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
        return {
            'owner': self.owner.as_dict_public(),
            'queue': [user.as_dict_public() for user in self.queue],
            'submitting_user': self.submitting_user.as_dict_public() if self.submitting_user is not None else None,
            'users_not_in_queue': [user.as_dict_public() for user in self.visitors.values() if user not in self.queue],
        }

    def __as_dict_private(self) -> dict:
        return {
            'owner': self.owner.as_dict_private(),
            'queue': [user.as_dict_private() for user in self.queue],
            'submitting_user': self.submitting_user.as_dict_private() if self.submitting_user is not None else None,
            'users_not_in_queue': [user.as_dict_private() for user in self.visitors.values() if user not in self.queue],
        }
