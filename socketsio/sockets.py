# sockets.py

import socket

from socketsio.protocols import (
    BaseProtocol, udp_socket, tcp_socket, is_udp,
    bluetooth_socket, is_tcp, is_tcp_bluetooth
)

from represent import represent

__all__ = [
    "Socket",
    "tcp_socket",
    "udp_socket",
    "bluetooth_socket"
]

Connection = socket.socket
Address = tuple[str, int]

@represent
class Socket:
    """A socket connection I/O object."""

    def __init__(
            self,
            protocol: BaseProtocol,
            connection: Connection = None,
            address: Address = None
    ) -> None:
        """
        Defines the attributes of a server.

        :param connection: The socket object of the server.
        :param protocol: The communication protocol object.
        :param address: The address of the connection.
        """

        self.connection = connection or protocol.socket()
        self.protocol = protocol
        self._address = address
    # end __init__

    @property
    def address(self) -> Address:
        """
        Returns the ip and port of the binding.

        :return: The address tuple.
        """

        return self._address
    # end address

    def is_tcp(self) -> bool:
        """
        Checks if the socket is a TCP socket.

        :return: The boolean flag.
        """

        return is_tcp(self.connection)
    # end is_tcp

    def is_udp(self) -> bool:
        """
        Checks if the socket is a UDP socket.

        :return: The boolean flag.
        """

        return is_udp(self.connection)
    # end is_udp

    def is_tcp_bluetooth(self) -> bool:
        """
        Checks if the socket is a UDP socket.

        :return: The boolean flag.
        """

        return is_tcp_bluetooth(self.connection)
    # end is_tcp_bluetooth

    def validate_connection(self) -> None:
        """Validates a connection."""

        if self.connection is None:
            self.connection = self.protocol.socket()
        # end if
    # end validate_connection

    def send(
            self,
            data: bytes,
            connection: Connection = None,
            address: Address = None
    ) -> tuple[bytes, Address | None]:
        """
        Sends a message to the client or server by its connection.

        :param data: The message to send to the client.
        :param connection: The sockets' connection object.
        :param address: The address of the sender.

        :return: The received message from the server.
        """

        return self.protocol.send(
            connection=connection or self.connection,
            data=data, address=address or self.address
        )
    # end send

    def receive(
            self,
            connection: Connection = None,
            address: Address = None
    ) -> tuple[bytes, Address | None]:
        """
        Receive a message from the client or server by its connection.

        :param connection: The sockets' connection object.
        :param address: The address of the sender.

        :return: The received message from the server.
        """

        data, new_address = self.protocol.receive(
            connection=connection or self.connection,
            address=address or self.address
        )

        if address is None and self.address is None:
            self._address = new_address
        # end if

        return data, new_address
    # end receive

    def close(self) -> None:
        """Closes the connection."""

        self.connection.close()
    # end close
# end Socket