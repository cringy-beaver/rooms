import asyncio
import websockets
import json


def print_dict(data: dict, offset: int = 0):
    if offset == 0:
        print('-' * 50)
    for key, value in data.items():
        if isinstance(value, dict):
            print(f'{" " * offset}{key}:')
            print_dict(value, offset + 4)
        else:
            print(f'{" " * offset}{key}: {value}')
    if offset == 0:
        print('-' * 50)


async def test():
    async with websockets.connect('ws://localhost:5002') as websocket:
        data_1 = {
            'action': 'create_room',
            'token': '1',
            'arg': {
                'tasks': [
                    {
                        'name': 'task1',
                        'url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
                    }
                ]
            }
        }

        await websocket.send(json.dumps(data_1))
        while True:
            response = await websocket.recv()
            print_dict(json.loads(response))


if __name__ == "__main__":
    asyncio.run(test())