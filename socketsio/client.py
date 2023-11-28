# client.py

from typing import Self
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
            reusable: bool = False
    ) -> None:
        """
        Defines the attributes of a server.

        :param connection: The socket object of the server.
        :param protocol: The communication protocol object.
        :param address: The address to save for the socket.
        :param reusable: The value to make the socket reusable.
        """

        super().__init__(
            connection=connection,
            protocol=protocol or BaseProtocol.protocol(),
            address=address,
            reusable=reusable
        )

        self._connected = False
    # end __init__

    @property
    def connected(self) -> bool:
        """
        Returns the value of a bounded connection.

        :return: The boolean flag.
        """

        return self._connected
    # end connected

    @property
    def preconnected(self) -> bool:
        """
        Returns the value of a bounded connection.

        :return: The boolean flag.
        """

        return self._address is not None
    # end preconnected

    def make_reusable(self) -> None:
        """Makes the socket reusable."""

        self._reusable = True
    # end make_reusable

    def make_unreusable(self) -> None:
        """Makes the socket unreusable."""

        self._reusable = False
    # end make_unreusable

    def connect(self, address: Address) -> None:
        """
        Returns the connection and address from the accepted client.

        :param address: The address of the server to connect to.
        """

        self.validate_connection()

        self.connection.connect(address)

        self._address = address

        self._connected = True
    # end connect

    def preconnect(self, address: Address) -> None:
        """
        Returns the connection and address from the accepted client.

        :param address: The address of the server to connect to.
        """

        self._address = address
    # end connect

    def reconnect(self) -> None:
        """Returns the connection and address from the accepted client."""

        self.connect(self._address)
    # end connect

    def validate_connected(self) -> None:
        """Validates a connection."""

        self.validate_connection()

        if not self.connected:
            if self.preconnected:
                self.reconnect()

            else:
                raise ValueError(
                    "Socket address is not defined "
                    "for automatic connection."
                )
            # end if
        # end if
    # end validate_connection

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

        return self.protocol.send(
            connection=connection or self.connection,
            data=data, address=address or self._address
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

        self.validate_connected()

        return self.protocol.receive(
            connection=connection or self.connection,
            address=address or self._address
        )
    # end receive

    def close(self) -> None:
        """Closes the connection."""

        super().close()

        self._connected = False
    # end close

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
    # end clone
# end Client