import websockets

from ..tools.status import Status, StatusEnum
from .switchboard import Switchboard


class SocketSwitchboard(Switchboard):
    async def send(self, data: str, _socket: websockets.WebSocketServerProtocol) -> Status:
        try:
            await _socket.send(data)
        except websockets.exceptions.ConnectionClosedOK:
            return Status(StatusEnum.FAILURE, "Connection closed")

        return Status(StatusEnum.SUCCESS, "Data sent")

    async def receive(self, _socket: websockets.WebSocketServerProtocol) -> Status[str]:
        try:
            data = await _socket.recv()
        except websockets.exceptions.ConnectionClosedOK:
            return Status(StatusEnum.FAILURE, "Connection closed")

        return Status(StatusEnum.SUCCESS, "Data received", data=data)

    async def send_and_receive(self, data: str, _socket: websockets.WebSocketServerProtocol) -> Status[str]:
        status = await self.send(data, _socket)
        if status.status == StatusEnum.FAILURE:
            return status

        return await self.receive(_socket)

    def close(self, _socket: websockets.WebSocketServerProtocol) -> Status:
        try:
            _socket.close()
        except websockets.exceptions.ConnectionClosedOK:
            return Status(StatusEnum.FAILURE, "Connection closed")

        return Status(StatusEnum.SUCCESS, "Connection closed")



