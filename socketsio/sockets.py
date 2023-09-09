# sockets.py

import socket
from typing import Optional, Tuple

from socketsio.protocols import (
    BaseProtocol, udp_socket, tcp_socket,
    base_socket, bluetooth_socket
)

__all__ = [
    "Socket",
    "base_socket",
    "tcp_socket",
    "udp_socket",
    "bluetooth_socket"
]

Connection = socket.socket
Address = Tuple[str, int]

class Socket:
    """A socket connection I/O object."""

    def __init__(
            self,
            protocol: BaseProtocol,
            connection: Optional[Connection] = None
    ) -> None:
        """
        Defines the attributes of a server.

        :param connection: The socket object of the server.
        :param protocol: The communication protocol object.
        """

        self.connection = connection or protocol.socket()
        self.protocol = protocol
    # end __init__

    def send(
            self,
            data: bytes,
            connection: Optional[Connection] = None,
            address: Optional[Address] = None
    ) -> None:
        """
        Sends a message to the client or server by its connection.

        :param data: The message to send to the client.
        :param connection: The sockets' connection object.
        :param address: The address of the sender.
        """

        self.protocol.send(
            connection=connection or self.connection,
            data=data, address=address
        )
    # end send

    def receive(
            self,
            connection: Optional[Connection] = None,
            address: Optional[Address] = None
    ) -> bytes:
        """
        Receive a message from the client or server by its connection.

        :param connection: The sockets' connection object.
        :param address: The address of the sender.

        :return: The received message from the server.
        """

        return self.protocol.receive(
            connection=connection or self.connection,
            address=address
        )
    # end receive

    def close(self) -> None:
        """Closes the connection."""

        self.connection.close()
    # end close
# end Socket