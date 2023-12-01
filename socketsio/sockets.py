# sockets.py

from typing import Self
import socket

from socketsio.protocols import (
    BaseProtocol, udp_socket, tcp_socket, is_udp,
    tcp_bluetooth_socket, is_tcp, is_tcp_bluetooth, is_udp_bluetooth
)

from represent import represent, Modifiers

__all__ = [
    "Socket",
    "tcp_socket",
    "udp_socket",
    "tcp_bluetooth_socket"
]

Connection = socket.socket
Address = tuple[str, int]
Output = tuple[bytes, Address | None]

@represent
class Socket:
    """A socket connection I/O object."""

    __modifiers__ = Modifiers(
        excluded=["connection"],
        properties=["reusable", "closed", "address"]
    )

    def __init__(
            self,
            protocol: BaseProtocol,
            connection: Connection = None,
            address: Address = None,
            reusable: bool = False
    ) -> None:
        """
        Defines the attributes of a server.

        :param connection: The socket object of the server.
        :param protocol: The communication protocol object.
        :param address: The address of the connection.
        :param reusable: The value to make the socket reusable.
        """

        self.connection = connection or protocol.socket()
        self.protocol = protocol
        self._reusable = reusable
        self._address = address

        self._closed = False

        self._connections_count = 1
    # end __init__

    @property
    def empty(self) -> bool:
        """
        Checks if the socket is empty.

        :return: The value of the connection.
        """

        return self.connection is None
    # end empty

    @property
    def closed(self) -> bool:
        """
        Checks if the socket is empty.

        :return: The value of the connection.
        """

        return self._closed
    # end closed

    @property
    def usable(self) -> bool:
        """
        Checks if the socket is usable.

        :return: The value of the connection.
        """

        return not self.empty or self.reusable
    # end usable

    @property
    def reusable(self) -> bool:
        """
        Checks if the socket is usable.

        :return: The value of the connection.
        """

        return self._reusable
    # end reusable

    @property
    def address(self) -> Address:
        """
        Returns the ip and port of the binding.

        :return: The address tuple.
        """

        return self._address
    # end address

    @property
    def connections_count(self) -> int:
        """
        Returns the connections count.

        :return: The count of connections made in the socket.
        """

        return self._connections_count
    # end connections_count

    def is_tcp(self) -> bool:
        """
        Checks if the socket is a TCP socket.

        :return: The boolean flag.
        """

        return is_tcp(self.connection or self.protocol.socket())
    # end is_tcp

    def is_udp(self) -> bool:
        """
        Checks if the socket is a UDP socket.

        :return: The boolean flag.
        """

        return is_udp(self.connection or self.protocol.socket())
    # end is_udp

    def is_tcp_bluetooth(self) -> bool:
        """
        Checks if the socket is a UDP socket.

        :return: The boolean flag.
        """

        return is_tcp_bluetooth(self.connection or self.protocol.socket())
    # end is_tcp_bluetooth

    def is_udp_bluetooth(self) -> bool:
        """
        Checks if the socket is a UDP socket.

        :return: The boolean flag.
        """

        return is_udp_bluetooth(self.connection or self.protocol.socket())
    # end is_udp_bluetooth

    def validate_open(self) -> None:
        """Validates that the socket is not closed."""

        if self.closed:
            raise ValueError(
                "Unable to operate using "
                f"{'an empty' if self.reusable else  'a used and non-reusable'}, "
                "server socket."
            )
        # end if
    # end validate_open

    def validate_connection(self) -> None:
        """Validates a connection."""

        if self.connection is None:
            if self.reusable:
                self.connection = self.protocol.socket()

                self._closed = False

                self._connections_count += 1

            elif self.connections_count > 0:
                raise ValueError(
                    "Only one connection is allowed on a non-reusable socket. "
                    "Consider making the socket reusable."
                )
            # end if
        # end if

        self.validate_open()
    # end validate_connection

    def send(
            self,
            data: bytes,
            connection: Connection = None,
            address: Address = None
    ) -> Output:
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
    ) -> Output:
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

        if self.reusable:
            self.connection = self.protocol.socket()

        else:
            self.connection = None

            self._closed = True
        # end if
    # end close

    def clone(self) -> Self:
        """
        Returns a copy of the socket wrapper object.

        :return: The new socket object.
        """

        return Socket(
            protocol=self.protocol,
            connection=self.protocol.socket(),
            address=self.address,
            reusable=self.reusable
        )
    # end clone
# end Socket