# subscriber.py

from looperation import Handler
from socketsio import Client

from socketsio.pubsub import ClientSubscriber, DataStore, Data

IP = "127.0.0.1"
PORT = 5080

def main() -> None:

    storage = DataStore()

    client = Client()
    client.connect((IP, PORT))

    subscriber = ClientSubscriber(socket=client, storage=storage)
    subscriber.queue_socket.run(block=False)

    subscriber.authenticate({'name': 'abc', 'password': '123'})

    print(Data.load(Data.decode(client.receive()[0])))

    subscriber.subscribe(['AAPL', "AMZN", "GOOG"])

    with Handler(
        exception_callback=lambda h: client.close(),
        exception_handler=print
    ):
        while True:
            print(subscriber.data())

if __name__ == "__main__":
    main()
