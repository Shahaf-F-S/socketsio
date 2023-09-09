# server.py

import socket
from typing import Tuple

from socketsio import Server, TCP, BaseProtocol

Connection = socket.socket
Address = Tuple[str, int]

def respond(
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

    while True:
        received = protocol.receive(connection=connection, address=address)
        if not received:
            continue
        # end if

        sent = f"server received from {address}: ".encode() + received

        protocol.send(connection=connection, data=sent, address=address)
    # end while
# end action

def main() -> None:
    """Runs the test to test the program."""

    host = "127.0.0.1"
    port = 5555

    protocol = TCP()

    server = Server(protocol)
    server.bind((host, port))
    server.serve(action=respond, block=False)
# end main

if __name__ == "__main__":
    main()
# end if