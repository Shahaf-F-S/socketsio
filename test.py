# test.py

import socket
from typing import Tuple

from socketsio import (
    Client, Server, BaseProtocol, BCP, TCP, UDP, handler
)

Connection = socket.socket
Address = Tuple[str, int]

def action(connection: Connection, address: Address, protocol: BaseProtocol) -> None:
    """
    Sets or updates clients data in the clients' container .

    :param protocol: The protocol to use for sockets communication.
    :param connection: The socket object of the server.
    :param address: The address of the connection.
    """

    with handler(exception_handler=print, cleanup_callback=connection.close):
        while True:
            received, address = protocol.receive(connection=connection, address=address)

            if not received:
                continue
            # end if

            print("server:", (received, address))

            sent = f"server received from {address}: ".encode() + received

            protocol.send(connection=connection, data=sent, address=address)
        # end while
    # end handler
# end action

HOST = "127.0.0.1"
PROTOCOL = 'UDP'
PORT = 5000

def main() -> None:
    """Tests the program."""

    if PROTOCOL == 'UDP':
        protocol = UDP()

    elif PROTOCOL == 'TCP':
        protocol = BCP(TCP())

    else:
        raise ValueError(f"Invalid protocol type: {PROTOCOL}")
    # end if

    server = Server(protocol)
    server.bind((HOST, PORT))
    server.serve(action=action, block=False)

    client = Client(protocol)
    client.connect((HOST, PORT))

    for _ in range(2):
        client.send(("hello world" * 1).encode())
        print("client:", client.receive())
    # end for
# end main

if __name__ == '__main__':
    main()
# end if