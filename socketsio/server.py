# server.py

import socket
from typing import Any, Callable
import threading

from socketsio.protocols import BaseProtocol
from socketsio.sockets import Socket

__all__ = [
    "Server",
    "ServerSideClient"
]

Connection = socket.socket
Address = tuple[str, int]
Action = Callable[[Socket], Any]
Output = tuple[bytes, Address | None]

class ServerSideClient(Socket):
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

        super().__init__(
            protocol=protocol,
            connection=connection,
            address=address,
            reusable=False
        )

        self._connected = self.connection is not None
    # end __init__

    @property
    def connected(self) -> bool:
        """
        Returns the value of the socket being connected.

        :return: The connected value.
        """

        return self._connected
    # end connected

    def close(self) -> None:
        """Closes the connection."""

        if not self.connected or not self.connection:
            return
        # end if

        if not self.is_udp():
            self.connection.close()

            self.connection = None
        # end if

        self._connected = False
    # end close

    def make_reusable(self) -> None:
        """Makes the socket reusable."""

        self._reusable = True
    # end make_reusable

    def make_unreusable(self) -> None:
        """Makes the socket unreusable."""

        self._reusable = False
    # end make_unreusable

    def validate_connection(self) -> None:
        """Validates a connection."""

        if not self.connected or not self.connection:
            raise ValueError("The socket is already closed.")
        # end if
    # end validate_connection
# end ServerSideClient

class Server(Socket):
    """A class to represent the server object."""

    DELAY = 0.0001

    def __init__(
            self,
            protocol: BaseProtocol = None,
            connection: Connection = None,
            address: Address = None,
            reusable: bool = False,
            sequential: bool = True,
    ) -> None:
        """
        Defines the attributes of a server.

        :param connection: The socket object of the server.
        :param protocol: The communication protocol object.
        :param sequential: The value to sequentially find clients.
        :param address: The address to save for the socket.
        :param reusable: The value to make the socket reusable.
        """

        if sequential is None:
            sequential = False
        # end if

        super().__init__(
            connection=connection,
            protocol=protocol or BaseProtocol.protocol(),
            address=address,
            reusable=reusable
        )

        self._listening = False
        self._bound = False

        self.sequential = sequential
    # end __init__

    @property
    def listening(self) -> bool:
        """
        Returns the value of an active listening process.

        :return: The boolean flag.
        """

        return self._listening
    # end listening

    @property
    def bound(self) -> bool:
        """
        Returns the value of a bounded connection.

        :return: The boolean flag.
        """

        return self._bound
    # end bound

    @property
    def prebound(self) -> bool:
        """
        Returns the value of a bounded connection.

        :return: The boolean flag.
        """

        return self._address is not None
    # end prebound

    def bind(self, address: Address) -> None:
        """
        Binds the connection of the server.

        :param address: The address to bind to.
        """

        self.validate_connection()

        self.connection.bind(address)

        self._address = address

        self._bound = True
    # end bind

    def prebind(self, address: Address) -> None:
        """
        Binds the connection of the server.

        :param address: The address to bind to.
        """

        self._address = address
    # end bind

    def rebind(self) -> None:
        """Binds the connection of the server."""

        self.bind(self._address)
    # end bind

    def validate_binding(self) -> None:
        """Validates the binding of the socket."""

        self.validate_connection()

        if not self.bound:
            if self.prebound:
                self.rebind()

            else:
                raise ValueError(
                    "Cannot start listening before binding."
                )
            # end if
        # end if
    # end validate_binding

    def validate_listening(self) -> None:
        """Validates the binding of the socket."""

        if not self.listening and not self.is_udp():
            self.listen()
        # end if
    # end validate_binding

    def accept(self) -> tuple[socket.socket, Address]:
        """
        Returns the connection and address from the accepted client.

        :return: The sockets object and the address.
        """

        self.validate_listening()

        return self.connection.accept()
    # end accept

    def _action_parameters(self, protocol: BaseProtocol = None) -> ServerSideClient:
        """
        Returns the parameters to call the action function.

        :return: The action parameters.
        """

        protocol = protocol or self.protocol

        if self.is_udp():
            connection, address = self.connection, None

        else:
            connection, address = self.accept()
        # end if

        return ServerSideClient(
            connection=connection,
            protocol=protocol,
            address=address
        )
    # end _action_parameters

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

        if not self.is_udp():
            raise ValueError(
                "Cannot directly send/receive "
                "with a non-UDP server socket."
            )
        # end if

        self.validate_binding()

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

        if not self.is_udp():
            raise ValueError(
                "Cannot directly send/receive "
                "with a non-UDP server socket."
            )
        # end if

        self.validate_binding()

        return self.protocol.receive(
            connection=connection or self.connection,
            address=address or self._address
        )
    # end receive

    def close(self) -> None:
        """Closes the connection."""

        super().close()

        self._listening = False
        self._bound = False
    # end close

    def action(self, client: Socket) -> None:
        """
        Sets or updates clients data in the clients' container .

        :param client: The client socket object.
        """
    # end action

    def listen(self) -> None:
        """Listens to clients."""

        self.validate_binding()

        self.connection.listen()

        self._listening = True
    # end listen

    def handle(
            self,
            protocol: BaseProtocol = None,
            action: Action = None,
            sequential: bool = None
    ) -> None:
        """
        Sends a message to the client by its connection.

        :param protocol: The protocol to use for sockets communication.
        :param action: The action to call.
        :param sequential: The value to sequentially find clients.
        """

        self.validate_listening()

        if sequential is not None:
            self.sequential = sequential
        # end if

        sequential = self.sequential

        if sequential:
            parameters = self._action_parameters(protocol=protocol)

            threading.Thread(target=lambda: action(parameters)).start()

        else:
            threading.Thread(
                target=lambda: action(
                    self._action_parameters(protocol=protocol)
                )
            ).start()
        # end if
    # end handle
# end Server