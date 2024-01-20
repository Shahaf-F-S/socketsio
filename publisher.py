# publisher.py

import time
import random

from looperation import Operator
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
        authenticate=lambda controller, data: Authorization(data.data in AUTHORIZED),
        on_unauthenticated=lambda controller, data: (time.sleep(0.5), controller.close()),
        on_join=lambda controller: print(f"client connected: {controller.socket.address}"),
        on_disconnect=lambda controller: print(f"client disconnected: {controller.socket.address}"),
    )

    server = Server()
    server.bind((IP, PORT))

    service = Operator(
        operation=lambda: server.handle(
            action=lambda _, socket: streamer.controller(
                socket=socket, exception_handler=print
            ).run(send=True, receive=True, block=True)
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
