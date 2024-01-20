# example.py

from socketsio import Client, Server, Socket

from looperation import Handler, Operator

def action(server: Server, client: Socket) -> None:

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
PORT = 5000

def main() -> None:
    """Tests the program."""

    server = Server()
    server.bind((HOST, PORT))

    service = Operator(
        operation=lambda: server.handle(action=action),
        stopping_collector=lambda: server.closed
    )
    service.run()

    client = Client()
    client.connect((HOST, PORT))

    for _ in range(2):
        client.send((", ".join(["hello world"] * 3)).encode())
        print("client:", client.receive())

    service.stop()
    client.close()
    server.close()

if __name__ == '__main__':
    main()
