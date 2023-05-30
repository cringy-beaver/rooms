from ..tools.status import Status, StatusEnum


class Task:
    def __init__(self, name: str, url: str, description: str = ""):
        self.name = name
        self.url = url
        self.description = description

    def __hash__(self):
        return hash(self.url)

    def as_dict(self) -> dict:
        return {
            'name': self.name,
            'url': self.url,
            'description': self.description
        }

    @staticmethod
    def from_dict(data: dict) -> Status['Task']:
        need_keys = ['name', 'url']
        for key in need_keys:
            if key not in data:
                return Status(StatusEnum.FAILURE, f"Key '{key}' not found")

        description = data['description'] if 'description' in data else ""

        return Status(StatusEnum.SUCCESS, "", data=Task(data['name'], data['url'], description))
