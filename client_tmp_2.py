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
    async with websockets.connect('ws://localhost:8000') as websocket:
        data_1 = {
            'action': 'join_room',
            'token': '2',
            'arg': {
                'room_id': '03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4'
            }
        }

        data_2 = {
            'action': 'get_task',
            'token': '2',
            'arg': {
                'room_id': '03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4'
            }
        }

        data_3 = {
            'action': 'join_queue',
            'token': '2',
            'arg': {
                'room_id': '03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4'
            }
        }

        for data in [data_1, data_2, data_3]:
            await websocket.send(json.dumps(data))
            response = await websocket.recv()
            print_dict(json.loads(response))


if __name__ == "__main__":
    asyncio.run(test())