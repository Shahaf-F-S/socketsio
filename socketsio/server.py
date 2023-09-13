# server.py

import socket
import time
from typing import Dict, Optional, List, Tuple, Any, Callable
import threading

from socketsio.protocols import BaseProtocol, is_tcp, is_tcp_bluetooth, is_udp
from socketsio.sockets import Socket

__all__ = [
    "Server"
]

Connection = socket.socket
Address = Tuple[str, int]
Action = Callable[[Connection, Address, BaseProtocol], Any]
Clients = Dict[Tuple[str, int], List[Connection]]

class Server(Socket):
    """A class to represent the server object."""

    DELAY = 0.0001

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

        super().__init__(connection=connection, protocol=protocol)

        self._listening = False
        self._bound = False

        self.handling = False

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

        if not self.is_udp() and (not self.listening):
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

    def handle(
            self,
            protocol: Optional[BaseProtocol] = None,
            action: Optional[Action] = None
    ) -> None:
        """
        Sends a message to the client by its connection.

        :param protocol: The protocol to use for sockets communication.
        :param action: The action to call.
        """

        protocol = protocol or self.protocol
        action = action or self.action

        if self.is_udp():
            connection, address = self.connection, None

        else:
            connection, address = self.accept()
        # end if

        action(connection, address, protocol)
    # end handle

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

    def _serve(
            self,
            protocol: Optional[BaseProtocol] = None,
            action: Optional[Action] = None
    ) -> None:
        """
        Runs the threads to serving_loop to clients with requests.

        :param action: The action to call.
        :param protocol: The protocol to use for sockets communication.
        """

        self.validate_listening()

        self.handling = True

        while self.handling:
            threading.Thread(
                target=lambda: self.handle(
                    protocol=protocol, action=action
                )
            ).start()
            break
        # end while
    # end _serve

    def serve(
            self,
            protocol: Optional[BaseProtocol] = None,
            action: Optional[Action] = None,
            block: Optional[bool] = True
    ) -> None:
        """
        Runs the threads to serving_loop to clients with requests.

        :param action: The action to call.
        :param protocol: The protocol to use for sockets communication.
        :param block: The value to block the process.
        """

        if block:
            self._serve(protocol=protocol, action=action)

        else:
            threading.Thread(
                target=lambda: self._serve(protocol=protocol, action=action)
            ).start()

            self.await_handling()
        # end if
    # end serve

    def await_handling(self) -> None:
        """Awaits the start of the handling process."""

        while not self.handling:
            time.sleep(self.DELAY)
        # end while
    # end await_handling
# end Server