from server.structures import Task


def test():
    task = Task("name", "url", "description")
    print(task.as_dict())
    print(Task.from_dict(task.as_dict()).data.as_dict())


if __name__ == "__main__":
    test()
