# subscriber.py

import json
import time
from typing import Iterable

from socketsio import SocketSenderQueue, Socket

from socketsio.pubsub.store import DataStore
from socketsio.pubsub.data import Data


__all__ = [
    "ClientSubscriber"
]

SUBSCRIBE = "subscribe"
UNSUBSCRIBE = "unsubscribe"
PAUSE = "pause"
UNPAUSE = "unpause"

RESPONSE = "response"
REQUEST = "request"

DATA = "data"

ACTION = "action"

class ClientSubscriber:

    def __init__(
            self,
            socket: Socket | SocketSenderQueue,
            storage: bool | DataStore = None
    ) -> None:

        if not isinstance(socket, SocketSenderQueue):
            queue_socket = SocketSenderQueue(socket)

        else:
            queue_socket = socket

        if storage is None:
            storage = DataStore()

        elif storage is False:
            storage = None

        self._queue_socket = queue_socket

        self.storage = storage

        self._paused = False
        self._events = set()

    @staticmethod
    def encode(data: dict[str, ...]) -> bytes:

        return json.dumps(data).encode()

    @staticmethod
    def decode(data: bytes) -> dict[str, ...]:

        return json.loads(data.decode())

    @property
    def queue_socket(self) -> SocketSenderQueue:

        return self._queue_socket

    @property
    def socket(self) -> Socket:

        return self.queue_socket.socket

    @property
    def paused(self) -> bool:

        return self._paused

    @property
    def events(self) -> set[str]:

        return self._events.copy()

    def subscribe(self, events: Iterable[str]) -> None:

        self.queue_socket.send(
            Data.encode(Data(name=SUBSCRIBE, time=time.time(), data=list(events)))
        )

        self._events.update(events)

    def unsubscribe(self, events: Iterable[str]) -> None:

        self.queue_socket.send(
            Data.encode(Data(name=UNSUBSCRIBE, time=time.time(), data=list(events)))
        )

        self._events.difference_update(events)

    def pause(self) -> None:

        self.queue_socket.send(Data.encode(Data(name=PAUSE, time=time.time())))
        
        self._paused = True

    def unpause(self) -> None:

        self.queue_socket.send(Data.encode(Data(name=UNPAUSE, time=time.time())))
        
        self._paused = False

    def data(
            self,
            insert: bool = True,
            load: bool = True
    ) -> Data:

        received = self.queue_socket.receive()[0]

        if not received:
            return Data()

        data = self.decode(received)

        if (
            load and
            (DATA in data) and
            isinstance(data[DATA], dict)
        ):
            data[DATA] = {
                key: Data(**values)
                for key, values in data[DATA].items()
            }

        if (
            insert and
            self.storage and
            (DATA in data) and
            isinstance(data[DATA], dict)
        ):
            self.storage.insert_all(
                (Data(**values) if not isinstance(values, Data) else values)
                for values in data[DATA].values()
            )

        return Data(**data)