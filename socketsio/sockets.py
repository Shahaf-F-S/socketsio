# sockets.py

from typing import Self, Callable, Any
import socket

from socketsio.protocols import (
    BaseProtocol, udp_socket, tcp_socket, is_udp,
    tcp_bluetooth_socket, is_tcp, is_tcp_bluetooth, is_udp_bluetooth
)

__all__ = [
    "Socket",
    "tcp_socket",
    "udp_socket",
    "tcp_bluetooth_socket"
]

Connection = socket.socket
Address = tuple[str, int]
Output = tuple[bytes, Address | None]

class Socket:
    """A socket connection I/O object."""

    def __init__(
            self,
            protocol: BaseProtocol,
            connection: Connection = None,
            address: Address = None,
            reusable: bool = False,
            on_init: Callable[[Self], Any] = None,
            on_send: Callable[[Self, bytes, Address | None], Any] = None,
            on_receive: Callable[[Self, bytes, Address | None], Any] = None,
            on_close: Callable[[Self], Any] = None
    ) -> None:
        """
        Defines the attributes of a server.

        :param connection: The socket object of the server.
        :param protocol: The communication protocol object.
        :param address: The address of the connection.
        :param reusable: The value to make the socket reusable.
        :param on_init: A callback to run on init.
        :param on_send: A callback to run on send.
        :param on_receive: A callback to run on receive.
        :param on_close: A callback to run on close.
        """

        self.connection = connection or protocol.socket()
        self.protocol = protocol

        self._reusable = reusable
        self._address = address

        self.on_init = on_init

        self.on_close = on_close
        self.on_send = on_send
        self.on_receive = on_receive

        self._closed = False

        self._connections_count = 1

        if self.on_init:
            self.on_init(self)

    @property
    def empty(self) -> bool:
        """
        Checks if the socket is empty.

        :return: The value of the connection.
        """

        return self.connection is None

    @property
    def closed(self) -> bool:
        """
        Checks if the socket is empty.

        :return: The value of the connection.
        """

        return self._closed

    @property
    def usable(self) -> bool:
        """
        Checks if the socket is usable.

        :return: The value of the connection.
        """

        return not self.empty or self.reusable

    @property
    def reusable(self) -> bool:
        """
        Checks if the socket is usable.

        :return: The value of the connection.
        """

        return self._reusable

    @property
    def address(self) -> Address:
        """
        Returns the ip and port of the binding.

        :return: The address tuple.
        """

        return self._address

    @property
    def connections_count(self) -> int:
        """
        Returns the connections count.

        :return: The count of connections made in the socket.
        """

        return self._connections_count

    def is_tcp(self) -> bool:
        """
        Checks if the socket is a TCP socket.

        :return: The boolean flag.
        """

        return is_tcp(self.connection or self.protocol.socket())

    def is_udp(self) -> bool:
        """
        Checks if the socket is a UDP socket.

        :return: The boolean flag.
        """

        return is_udp(self.connection or self.protocol.socket())

    def is_tcp_bluetooth(self) -> bool:
        """
        Checks if the socket is a UDP socket.

        :return: The boolean flag.
        """

        return is_tcp_bluetooth(self.connection or self.protocol.socket())

    def is_udp_bluetooth(self) -> bool:
        """
        Checks if the socket is a UDP socket.

        :return: The boolean flag.
        """

        return is_udp_bluetooth(self.connection or self.protocol.socket())

    def validate_open(self) -> None:
        """Validates that the socket is not closed."""

        if self.closed:
            raise ValueError(
                "Unable to operate using "
                f"{'an empty' if self.reusable else  'a used and non-reusable'}, "
                "server socket."
            )

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

        self.validate_open()

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

        output = self.protocol.send(
            connection=connection or self.connection,
            data=data, address=address or self.address
        )

        if self.on_send:
            self.on_send(self, *output)

        return output

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

        if self.on_receive:
            self.on_receive(self, data, new_address)

        return data, new_address

    def close(self) -> None:
        """Closes the connection."""

        if self.closed:
            return

        self.connection.close()

        if self.reusable:
            self.connection = self.protocol.socket()

        else:
            self.connection = None

            self._closed = True

        if self.on_close:
            self.on_close(self)

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
