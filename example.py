# example.py

import socket
from typing import Tuple

from socketsio import Client, Server, Socket

from looperator import Handler, Operator

Connection = socket.socket
Address = Tuple[str, int]

def action(client: Socket) -> None:
    """
    Sets or updates clients data in the clients' container .

    :param client: The client socket object.
    """

    with Handler(
        exception_handler=print,
        cleanup_callback=client.close
    ):
        while True:
            received, address = client.receive()

            if not received:
                continue
            # end if

            print("server:", (received, address))

            sent = (
                f"server received from "
                f"{address}: ".encode() + received
            )

            client.send(sent)
        # end while
    # end handler
# end action

HOST = "127.0.0.1"
PORT = 5000

def main() -> None:
    """Tests the program."""

    server = Server()
    server.bind((HOST, PORT))

    service = Operator(operation=lambda: server.handle(action=action))
    service.run()

    client = Client()
    client.connect((HOST, PORT))

    for _ in range(2):
        client.send((", ".join(["hello world"] * 3)).encode())
        print("client:", client.receive())
    # end for
# end main

if __name__ == '__main__':
    main()
# end if