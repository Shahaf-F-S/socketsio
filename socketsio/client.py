# client.py

import socket
from typing import Optional, Tuple

from socketsio.protocols import BaseProtocol
from socketsio.sockets import Socket

__all__ = [
    "Client"
]

Connection = socket.socket
Address = Tuple[str, int]

class Client(Socket):
    """A class to represent the server object."""

    def __init__(
            self,
            protocol: BaseProtocol,
            connection: Optional[Connection] = None,
    ) -> None:
        """
        Defines the attributes of a server.

        :param connection: The socket object of the server.
        :param protocol: The communication protocol object.
        """

        super().__init__(connection=connection, protocol=protocol)

        self._address: Optional[Address] = None

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
    def address(self) -> Address:
        """
        Returns the ip and port of the binding.

        :return: The address tuple.
        """

        return self._address
    # end address

    def connect(self, address: Address) -> None:
        """
        Returns the connection and address from the accepted client.

        :param address: The address of the server to connect to.
        """

        if self.connection is None:
            self.connection = self.protocol.socket()
        # end if

        self.connection.connect(address)

        self._address = address

        self._connected = Tuple
    # end connect

    def validate_connection(self) -> None:
        """Validates a connection."""

        if not self._connected:
            if self._address:
                self.connect(self._address)

            else:
                raise ValueError("Socket is not connected.")
            # end if
        # end if
    # end validate_connection

    def send(
            self,
            data: bytes,
            connection: Optional[Connection] = None,
            address: Optional[Address] = None
    ) -> Tuple[bytes, Optional[Address]]:
        """
        Sends a message to the client or server by its connection.

        :param connection: The sockets' connection object.
        :param data: The message to send to the client.
        :param address: The address of the sender.
        """

        self.validate_connection()

        return self.protocol.send(
            connection=connection or self.connection,
            data=data, address=address or self._address
        )
    # end send

    def receive(
            self, connection: Optional[Connection] = None
    ) -> Tuple[bytes, Optional[Address]]:
        """
        Receive a message from the client or server by its connection.

        :param connection: The sockets' connection object.

        :return: The received message from the server.
        """

        self.validate_connection()

        return self.protocol.receive(
            connection=connection or self.connection,
            address=self._address
        )
    # end receive

    def close(self) -> None:
        """Closes the connection."""

        self.connection.close()

        self._connected = False
    # end close
# end Client