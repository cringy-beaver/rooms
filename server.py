import asyncio
import websockets

from .server.core import Core
from .server.network_structures import SocketSwitchboard
from .server.tools.status import Status, StatusEnum

CORE = Core(SocketSwitchboard())


async def listen(websocket: websockets.WebSocketServerProtocol) -> None:
    try:
        while True:
            data = await websocket.recv()
            response = await CORE.handle_request(data, websocket)

            if response.status == ...:
                ...

    except websockets.exceptions.ConnectionClosedOK:
        ...
    except Exception as e:
        ...


async def main():
    server = await websockets.serve(listen, "localhost", 8000)
    await server.wait_closed()


if __name__ == "__main__":
    asyncio.run(main())
