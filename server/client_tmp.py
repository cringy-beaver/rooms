import asyncio
import websockets


async def test():
    async with websockets.connect('ws://localhost:8000') as websocket:
        await websocket.send("hello")
        while True:
            response = await websocket.recv()
            print(response)


if __name__ == "__main__":
    asyncio.run(test())