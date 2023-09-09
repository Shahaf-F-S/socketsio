# service.py

import socket
import datetime as dt
from typing import Dict, Optional, List, Tuple, Any, Callable, Union
import threading

from socketsio.protocols import BaseProtocol
from socketsio.interface import ServiceInterface
from socketsio.server import Server

__all__ = [
    "Service"
]

Connection = socket.socket
Address = Tuple[str, int]
Action = Callable[[Connection, Address, BaseProtocol], Any]
Clients = Dict[Tuple[str, int], List[Connection]]

class Service(ServiceInterface):
    """The server object to control the communication ith multiple clients."""

    __slots__ = "server",

    def __init__(self, server: Server) -> None:
        """
        Defines the server attribute.

        :param server: The server object.
        """

        super().__init__()

        self.server = server
    # end __init__

    def run(
            self,
            protocol: Optional[BaseProtocol] = None,
            action: Optional[Action] = None,
            clients: Optional[Clients] = None,
            remove: Optional[bool] = True,
            update: Optional[bool] = False,
            block: Optional[bool] = False,
            refresh: Optional[Union[float, dt.timedelta]] = None,
            wait: Optional[Union[float, dt.timedelta, dt.datetime]] = None,
            timeout: Optional[Union[float, dt.timedelta, dt.datetime]] = None,
    ) -> None:
        """
        Runs the process of the service.

        :param action: The action to call.
        :param protocol: The protocol to use for sockets communication.
        :param clients: The client's collection.
        :param remove: The value to remove clients after each response.
        :param update: The value to update the service.
        :param block: The value to block the execution and wain for the service.
        :param refresh: The value to refresh the service.
        :param wait: The waiting time.
        :param timeout: The start_timeout for the process.
        """

        threading.Thread(
            target=lambda: self.server.serve(
                block=True, protocol=protocol, action=action,
                clients=clients, remove=remove
            )
        ).start()

        super().run(
            update=update, block=block, refresh=refresh,
            wait=wait, timeout=timeout
        )
    # end run

    def stop(self) -> None:
        """Stops the service."""

        super().stop()

        self.server.handling = False
    # end stop
# end ServerService