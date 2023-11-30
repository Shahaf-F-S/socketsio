# queue.py

import datetime as dt
from typing import Callable, Any
import socket as _socket

from looperator import Operator, Handler

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
    # end __init__

    @property
    def address(self) -> Address:
        """
        Returns the ip and port of the binding.

        :return: The address tuple.
        """

        return self.socket.address
    # end address

    def is_tcp(self) -> bool:
        """
        Checks if the socket is a TCP socket.

        :return: The boolean flag.
        """

        return self.socket.is_tcp()
    # end is_tcp

    def is_udp(self) -> bool:
        """
        Checks if the socket is a UDP socket.

        :return: The boolean flag.
        """

        return self.socket.is_udp()
    # end is_udp

    def is_tcp_bluetooth(self) -> bool:
        """
        Checks if the socket is a UDP socket.

        :return: The boolean flag.
        """

        return self.socket.is_tcp_bluetooth()
    # end is_tcp_bluetooth

    def validate_connection(self) -> None:
        """Validates a connection."""

        self.socket.validate_connection()
    # end validate_connection

    def send_queue(self) -> None:
        """Sends the message from the queue"""

        if self.queue:
            try:
                data = self.queue.pop(0)

                if data[0]:
                    self.socket.send(*data)
                # end if

            except IndexError:
                pass
            # end try
        # end if
    # end send_queue

    def send_all_queue(self) -> None:
        """Sends the message from the queue"""

        while self.queue:
            self.send_queue()
        # end while
    # end send_all_queue

    def receive(self, address: Address = None) -> tuple[bytes, Address | None]:
        """
        Receive a message from the client or server by its connection.

        :param address: The address of the sender.

        :return: The received message from the server.
        """

        return self.socket.receive(address)
    # end receive

    def send(self, data: bytes, address: Address = None) -> tuple[bytes, Address | None]:
        """
        Sends a message to the client or server by its connection.

        :param data: The message to send to the client.
        :param address: The address of the sender.

        :return: The received message from the server.
        """

        self.queue.append((data, address))

        return data, address
    # end send

    def close(self) -> None:
        """Closes the connection."""

        self.socket.close()
    # end close
# end SocketQueue