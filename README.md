# sockets-io

> A python wrapper around the builtin socket module, for generalized communication protocols, unified socket interface, utility methods, and modular protocol swapping capeabilities. Including a socket based Pub/Sub system.

## examples

basic server socket threading based

```python
from socketsio import Server, Socket, BHP, TCP, UDP

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
PROTOCOL = 'TCP'
PORT = 5000

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
```

basic client socket

```python
from socketsio import Client, BHP, TCP, UDP

HOST = "127.0.0.1"
PROTOCOL = 'TCP'
PORT = 5000

if PROTOCOL == 'UDP':
    protocol = UDP()

elif PROTOCOL == 'TCP':
    protocol = BHP(TCP())

else:
    raise ValueError(f"Invalid protocol type: {PROTOCOL}")

client = Client(protocol)
client.connect((HOST, PORT))

for _ in range(2):
    client.send((", ".join(["hello world"] * 3)).encode())
    print("client:", client.receive())

```

pubsub server with authentication

```python
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
```

pubsub client with authentication

```python
from looperation import Handler
from socketsio import Client

from socketsio.pubsub import ClientSubscriber, DataStore, Data

IP = "127.0.0.1"
PORT = 5080

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
```