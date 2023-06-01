from .task import Task

from datetime import datetime


class User:
    def __init__(self, name: str, second_name: str, id: str):
        self.name = name
        self.second_name = second_name
        self.id = id

        self.task: Task = None
        self.task_time: datetime = None

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        if not isinstance(other, User):
            return False

        return self.id == other.id

    def set_task(self, task: Task) -> None:
        self.task = task
        self.task_time = datetime.now()

    def as_dict_private(self) -> dict:
        return {
            'name': self.name,
            'second_name': self.second_name,
            'id': self.id,
            'task': self.task.as_dict() if self.task else None,
            'task_time': self.task_time.strftime("%d.%m.%Y %H:%M:%S") if self.task_time else None
        }

    def as_dict_public(self) -> dict:
        return {
            'name': self.name,
            'second_name': self.second_name
        }

    def initials(self) -> str:
        return f"{self.name} {self.second_name}"
