import asyncio

import websockets

sockets = set()
# create handler for each connection


async def listen(websocket: websockets.WebSocketServerProtocol, path: str) -> None:
    sockets.add(websocket)

    try:
        while True:
            data = await websocket.recv()
            print(data)

            for socket in sockets:
                await socket.send(data)
    except websockets.exceptions.ConnectionClosedOK:
        print("Connection closed")
        sockets.remove(websocket)
    except Exception as e:
        print(e)
        sockets.remove(websocket)



    # data = await websocket.recv()
    #
    # reply = f"Data recieved as:  {data}!"
    # print(reply)
    #
    # await websocket.send(reply)
    # client_socket = websocket



async def main():
    # create server
    server = await websockets.serve(listen, "localhost", 8000)

    # wait for server to close
    await server.wait_closed()


if __name__ == "__main__":
    asyncio.run(main())
