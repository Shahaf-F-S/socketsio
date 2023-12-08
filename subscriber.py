# subscriber.py

from looperator import Handler
from socketsio import Client

from socketsio.pubsub import ClientSubscriber, DataStore


IP = "127.0.0.1"
PORT = 5080

def main() -> None:

    storage = DataStore()

    client = Client()
    client.connect((IP, PORT))

    subscriber = ClientSubscriber(socket=client, storage=storage)
    subscriber.queue_socket.run(block=False)
    subscriber.subscribe(['AAPL', "AMZN", "GOOG"])

    with Handler(
        exception_callback=client.close,
        exception_handler=print
    ):
        while True:
            print(subscriber.data())


if __name__ == "__main__":
    main()
