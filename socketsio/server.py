# server.py

import socket
from typing import (
    Optional, Tuple, Any, Callable
)
import threading

from socketsio.protocols import BaseProtocol
from socketsio.sockets import Socket

__all__ = [
    "Server"
]

Connection = socket.socket
Address = Tuple[str, int]
Action = Callable[[Connection, Optional[Address], Optional[BaseProtocol]], Any]

class Server(Socket):
    """A class to represent the server object."""

    DELAY = 0.0001

    def __init__(
            self,
            protocol: BaseProtocol,
            connection: Optional[Connection] = None,
            sequential: Optional[bool] = False
    ) -> None:
        """
        Defines the attributes of a server.

        :param connection: The socket object of the server.
        :param protocol: The communication protocol object.
        :param sequential: The value to sequentially find clients.
        """

        if sequential is None:
            sequential = False
        # end if

        super().__init__(connection=connection, protocol=protocol)

        self._listening = False
        self._bound = False

        self.sequential = sequential

        self._address: Optional[Address] = None
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
    def address(self) -> Address:
        """
        Returns the ip and port of the binding.

        :return: The address tuple.
        """

        return self._address
    # end address

    def bind(self, address: Address) -> None:
        """
        Binds the connection of the server.

        :param address: The address to bind to.
        """

        self.connection.bind(address)

        self._address = address

        self._bound = True
    # end bind

    def validate_binding(self) -> None:
        """Validates the binding of the socket."""

        if not self.bound:
            raise ValueError("Cannot start listening before binding.")
        # end if
    # end validate_binding

    def validate_listening(self) -> None:
        """Validates the binding of the socket."""

        if not self.listening and not self.is_udp():
            self.listen()
        # end if
    # end validate_binding

    def accept(self) -> Tuple[socket.socket, Address]:
        """
        Returns the connection and address from the accepted client.

        :return: The sockets object and the address.
        """

        self.validate_listening()

        return self.connection.accept()
    # end accept

    def action_parameters(
            self, protocol: Optional[BaseProtocol] = None
    ) -> Tuple[Connection, Address, BaseProtocol]:
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

        return connection, address, protocol
    # end action_parameters

    def _handle(
            self,
            protocol: Optional[BaseProtocol] = None,
            action: Optional[Action] = None
    ) -> None:
        """
        Sends a message to the client by its connection.

        :param protocol: The protocol to use for sockets communication.
        :param action: The action to call.
        """

        action(*self.action_parameters(protocol=protocol))
    # end _handle

    def action(
            self,
            connection: Connection,
            address: Address,
            protocol: BaseProtocol
    ) -> None:
        """
        Sets or updates clients data in the clients' container .

        :param protocol: The protocol to use for sockets communication.
        :param connection: The socket object of the server.
        :param address: The address of the connection.
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
            protocol: Optional[BaseProtocol] = None,
            action: Optional[Action] = None,
            sequential: Optional[bool] = None
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
            parameters = self.action_parameters(protocol=protocol)

            threading.Thread(
                target=lambda: action(*parameters)
            ).start()

        else:
            threading.Thread(
                target=lambda: self._handle(
                    protocol=protocol, action=action
                )
            ).start()
        # end if
    # end handle
# end Server