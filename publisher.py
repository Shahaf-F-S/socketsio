# publisher.py

import time
import random

from looperator import Operator
from socketsio import Server

from socketsio.pubsub import DataStore, Data, SubscriptionStreamer, Authorization


IP = "127.0.0.1"
PORT = 5080

DELAY = 0.00001

AUTHORIZED = [
    {'name': 'abc', 'password': '123'}
]

class Producer:

    ACTION = "action"
    BUY = "buy"
    SELL = "sell"

    NAMES = ['AAPL', "AMZN", "GOOG", "TSLA", "META"]
    BUY_DATA = {ACTION: BUY}
    SELL_DATA = {ACTION: SELL}

    def next(self) -> Data:

        return Data(
            name=random.choice(self.NAMES),
            data=random.choice((self.BUY_DATA, self.SELL_DATA)),
            time=time.time()
        )


def main() -> None:

    storage = DataStore()

    producer = Producer()

    screener = Operator(
        operation=lambda: storage.insert(producer.next()),
        delay=DELAY
    )

    streamer = SubscriptionStreamer(
        storage=storage,
        authenticate=lambda data: Authorization(data.data in AUTHORIZED)
    )

    server = Server()
    server.bind((IP, PORT))

    service = Operator(
        operation=lambda: server.handle(
            action=lambda _, socket: (
                print(f"client connected: {socket.address}"),
                streamer.controller(
                    socket=socket,
                    exception_handler=print
                ).run(send=True, receive=True, block=True),
                print(f"client disconnected: {socket.address}")
            )
        ),
        termination=lambda: (
            print("disconnecting server"),
            server.close(),
            print("server disconnected")
        )
    )

    screener.run(block=False)
    service.run(block=True)


if __name__ == "__main__":
    main()
