# client.py

from typing import Self, Callable, Any
import socket

from socketsio.protocols import BaseProtocol
from socketsio.sockets import Socket

__all__ = [
    "Client"
]

Connection = socket.socket
Address = tuple[str, int]
Output = tuple[bytes, Address | None]

class Client(Socket):
    """A class to represent the server object."""

    def __init__(
            self,
            protocol: BaseProtocol = None,
            connection: Connection = None,
            address: Address = None,
            reusable: bool = False,
            on_init: Callable[[Self], Any] = None,
            on_connect: Callable[[Self], Any] = None,
            on_send: Callable[[Self, bytes, Address | None], Any] = None,
            on_receive: Callable[[Self, bytes, Address | None], Any] = None,
            on_close: Callable[[Self], Any] = None,
    ) -> None:
        """
        Defines the attributes of a server.

        :param connection: The socket object of the server.
        :param protocol: The communication protocol object.
        :param address: The address to save for the socket.
        :param reusable: The value to make the socket reusable.
        :param on_init: A callback to run on init.
        :param on_connect: A callback to run on connect.
        :param on_close: A callback to run on close.
        """

        super().__init__(
            connection=connection,
            protocol=protocol or BaseProtocol.protocol(),
            address=address,
            reusable=reusable,
            on_init=on_init,
            on_close=on_close,
            on_send=on_send,
            on_receive=on_receive
        )

        self.on_connect = on_connect

        self._connected = False

    @property
    def connected(self) -> bool:
        """
        Returns the value of a bounded connection.

        :return: The boolean flag.
        """

        return self._connected

    @property
    def preconnected(self) -> bool:
        """
        Returns the value of a bounded connection.

        :return: The boolean flag.
        """

        return self._address is not None

    def make_reusable(self) -> None:
        """Makes the socket reusable."""

        self._reusable = True

    def make_unreusable(self) -> None:
        """Makes the socket unreusable."""

        self._reusable = False

    def connect(self, address: Address) -> None:
        """
        Returns the connection and address from the accepted client.

        :param address: The address of the server to connect to.
        """

        self.validate_connection()

        self.connection.connect(address)

        self._address = address

        self._connected = True

        if self.on_connect:
            self.on_connect(self)

    def preconnect(self, address: Address) -> None:
        """
        Returns the connection and address from the accepted client.

        :param address: The address of the server to connect to.
        """

        self._address = address

    def reconnect(self) -> None:
        """Returns the connection and address from the accepted client."""

        self.connect(self._address)

    def validate_connected(self) -> None:
        """Validates a connection."""

        self.validate_connection()

        if not self.is_udp() and not self.connected:
            if self.preconnected:
                self.reconnect()

            else:
                raise ValueError(
                    "Socket address is not defined "
                    "for automatic connection."
                )

    def send(
            self,
            data: bytes,
            connection: Connection = None,
            address: Address = None
    ) -> Output:
        """
        Sends a message to the client or server by its connection.

        :param connection: The sockets' connection object.
        :param data: The message to send to the client.
        :param address: The address of the sender.

        :return: The received message from the server.
        """

        self.validate_connected()

        return super().send(
            connection=connection or self.connection,
            data=data, address=address or self._address
        )

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

        self.validate_connected()

        return super().receive(
            connection=connection or self.connection,
            address=address or self._address
        )

    def close(self) -> None:
        """Closes the connection."""

        saved_on_close = self.on_close
        self.on_close = None

        super().close()

        self._connected = False

        self.on_close = saved_on_close

        if self.on_close:
            self.on_close(self)

    def clone(self) -> Self:
        """
        Returns a copy of the socket wrapper object.

        :return: The new socket object.
        """

        return Client(
            protocol=self.protocol,
            connection=self.protocol.socket(),
            address=self.address,
            reusable=self.reusable
        )
