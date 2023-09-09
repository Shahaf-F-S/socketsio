# server.py

import socket
import time
from typing import Dict, Optional, List, Tuple, Any, Callable, Union
import threading

from socketsio.protocols import BaseProtocol
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
            connection: Optional[Connection] = None,
            clients: Optional[Union[Clients, bool]] = None
    ) -> None:
        """
        Defines the attributes of a server.

        :param connection: The socket object of the server.
        :param protocol: The communication protocol object.
        :param clients: The client's collection.
        """

        super().__init__(connection=connection, protocol=protocol)

        if clients in (True, None):
            clients = {}

        elif clients is False:
            clients = None
        # end if

        self.clients: Optional[Clients] = clients

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

        if not self.listening:
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
            action: Optional[Action] = None,
            clients: Optional[Clients] = None,
            remove: Optional[bool] = True
    ) -> None:
        """
        Sends a message to the client by its connection.

        :param protocol: The protocol to use for sockets communication.
        :param action: The action to call.
        :param clients: The client's collection.
        :param remove: The value to remove clients after each response.
        """

        if clients is None:
            clients = self.clients
        # end if

        protocol = protocol or self.protocol
        action = action or self.action

        connection, address = self.accept()

        if clients is not None:
            clients.setdefault(address, []).append(connection)
        # end if

        action(connection, address, protocol)

        if remove and (clients is not None):
            clients.get(address).remove(connection)

            if not clients.get(address):
                clients.pop(address)
            # end if
        # end if
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
            action: Optional[Action] = None,
            clients: Optional[Clients] = None,
            remove: Optional[bool] = True
    ) -> None:
        """
        Runs the threads to serving_loop to clients with requests.

        :param action: The action to call.
        :param protocol: The protocol to use for sockets communication.
        :param clients: The client's collection.
        :param remove: The value to remove clients after each response.
        """

        if clients is None:
            clients = self.clients
        # end if

        self.validate_listening()

        self.handling = True

        while self.handling:
            threading.Thread(
                target=lambda: self.handle(
                    clients=clients, remove=remove,
                    protocol=protocol, action=action
                )
            ).start()
        # end while
    # end _serve

    def serve(
            self,
            protocol: Optional[BaseProtocol] = None,
            action: Optional[Action] = None,
            clients: Optional[Clients] = None,
            remove: Optional[bool] = True,
            block: Optional[bool] = True
    ) -> None:
        """
        Runs the threads to serving_loop to clients with requests.

        :param action: The action to call.
        :param protocol: The protocol to use for sockets communication.
        :param clients: The client's collection.
        :param remove: The value to remove clients after each response.
        :param block: The value to block the process.
        """

        parameters = dict(
            protocol=protocol, action=action,
            clients=clients, remove=remove
        )

        if block:
            self._serve(**parameters)

        else:
            threading.Thread(
                target=lambda: self._serve(**parameters)
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