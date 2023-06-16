import asyncio
import websockets
import json

from server.controller_stuff.controller import Controller

CONTROLLER: Controller[websockets.WebSocketServerProtocol] = Controller()


async def listen(websocket: websockets.WebSocketServerProtocol) -> None:
    while True:
        try:
            data = await websocket.recv()
        except websockets.exceptions.ConnectionClosedOK:
            break

        try:
            data = json.loads(data)
        except json.JSONDecodeError:
            await websocket.send(
                json.dumps(
                    {
                        'action': 'unknown',
                        'status': 'FAILURE',
                        'message': 'Bad json',
                        'data': {}
                    }
                )
            )

            continue

        response = await CONTROLLER.handle_request(data, websocket)

        for data, _websocket in response:
            try:
                await _websocket.send(json.dumps(data))
            except websockets.exceptions.ConnectionClosedOK:
                pass
            except Exception as e:
                pass


async def main():
    server = await websockets.serve(listen, "0.0.0.0", 5002)
    await server.wait_closed()


if __name__ == "__main__":
    asyncio.run(main())
