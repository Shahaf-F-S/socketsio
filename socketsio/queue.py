# queue.py

import datetime as dt
from typing import Callable, Any
import socket as _socket

from looperation import Operator, Handler

from socketsio.sockets import Socket

__all__ = [
    "SocketSenderQueue"
]

Connection = _socket.socket
Address = tuple[str, int]

class SocketSenderQueue(Operator):
    """
    A class to schedule and manage sending and receiving
    messages across multiple processes.
    """

    def __init__(
            self,
            socket: Socket,
            queue: list[tuple[bytes, Address | None]] = None,
            termination: Callable[[], Any] = None,
            handler: Handler = None,
            loop: bool = True,
            delay: float | dt.timedelta = None,
            block: bool = False,
            wait: float | dt.timedelta | dt.datetime = None,
            timeout: float | dt.timedelta | dt.datetime = None
    ) -> None:
        """
        Defines the attributes of the socket sender queue.

        :param socket: The base socket object.
        :param queue: The queue object.
        :param termination: The termination callback.
        :param handler: The handler object to handle the operation.
        :param loop: The value to run a loop.
        :param delay: The delay for the process.
        :param wait: The value to wait after starting to run the process.
        :param block: The value to block the execution.
        :param timeout: The valur to add a start_timeout to the process.
        """

        self.socket = socket

        self.queue = queue or []

        super().__init__(
            operation=self.send_queue,
            termination=termination,
            handler=handler,
            loop=loop,
            delay=delay,
            block=block,
            wait=wait,
            timeout=timeout
        )

    def send_queue(self) -> None:
        """Sends the message from the queue"""

        if self.queue:
            try:
                data = self.queue.pop(0)

                if data[0]:
                    self.socket.send(*data)

            except IndexError:
                pass

    def send_all_queue(self) -> None:
        """Sends the message from the queue"""

        while self.queue:
            self.send_queue()

    def receive(self, address: Address = None) -> tuple[bytes, Address | None]:
        """
        Receive a message from the client or server by its connection.

        :param address: The address of the sender.

        :return: The received message from the server.
        """

        return self.socket.receive(address)

    def send(self, data: bytes, address: Address = None) -> tuple[bytes, Address | None]:
        """
        Sends a message to the client or server by its connection.

        :param data: The message to send to the client.
        :param address: The address of the sender.

        :return: The received message from the server.
        """

        self.queue.append((data, address))

        return data, address

    def close(self) -> None:
        """Closes the connection."""

        self.stop()

        self.socket.close()
