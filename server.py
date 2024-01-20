# server.py

from socketsio import Server, Socket, BHP, TCP, UDP

from looperation import Handler, Operator

def action(server: Server, client: Socket) -> None:
    """
    Sets or updates clients data in the clients' container .

    :param server: The server controlling the communication.
    :param client: The client socket object.
    """

    with Handler(
        exception_handler=print,
        cleanup_callback=lambda h: client.close()
    ):
        while not (client.closed or server.closed):
            received, address = client.receive()

            if not received:
                continue

            print("server:", (received, address))

            sent = (
                f"server received from "
                f"{address}: ".encode() + received
            )

            client.send(sent)

HOST = "127.0.0.1"
PROTOCOL = 'TCP'
PORT = 5000

def main() -> None:
    """Tests the program."""

    if PROTOCOL == 'UDP':
        protocol = UDP()

    elif PROTOCOL == 'TCP':
        protocol = BHP(TCP())

    else:
        raise ValueError(f"Invalid protocol type: {PROTOCOL}")

    server = Server(protocol)
    server.bind((HOST, PORT))

    service = Operator(
        operation=lambda: server.handle(action=action)
    )
    service.run()

if __name__ == '__main__':
    main()
