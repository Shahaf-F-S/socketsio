# test.py

import socket
from typing import Tuple

from socketsio import (
    Server, BaseProtocol,
    UDP, BCP, TCP, server_receive_from_client
)

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
        try:
            received, address = server_receive_from_client(
                connection=connection, protocol=protocol, address=address
            )

        except (
                ConnectionError,
                ConnectionRefusedError,
                ConnectionAbortedError,
                ConnectionResetError
        ) as e:
            print(f"{type(e).__name__}: {str(e)}")

            break
        # end try

        if not received:
            continue
        # end if

        sent = f"server received from {address}: ".encode() + received

        protocol.send(connection=connection, data=sent, address=address)
    # end while
# end respond

HOST = "127.0.0.1"
PROTOCOL = 'UDP'
PORT = 5000

def main() -> None:
    """Tests the program."""

    if PROTOCOL == 'UDP':
        protocol = BCP(UDP())

    elif PROTOCOL == 'TCP':
        protocol = BCP(TCP())

    else:
        raise ValueError(f"Invalid protocol type: {PROTOCOL}")
    # end if

    server = Server(protocol)
    server.bind((HOST, PORT))
    server.serve(action=respond, block=False)
# end main

if __name__ == '__main__':
    main()
# end if