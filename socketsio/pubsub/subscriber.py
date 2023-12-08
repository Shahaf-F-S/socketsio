# subscriber.py

import time
from typing import Iterable

from socketsio import SocketSenderQueue, Socket

from socketsio.pubsub.store import DataStore
from socketsio.pubsub.data import Data
from socketsio.pubsub.streamer import PAUSE, UNPAUSE, SUBSCRIBE, UNSUBSCRIBE


__all__ = [
    "ClientSubscriber"
]

class ClientSubscriber:
    """A class to represent a client subscriber object."""

    def __init__(
            self,
            socket: Socket | SocketSenderQueue,
            storage: bool | DataStore = None
    ) -> None:
        """
        Defines the attributes of the object.

        :param socket: The socket object.
        :param storage: The storage object.
        """

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

    @property
    def queue_socket(self) -> SocketSenderQueue:
        """
        Returns the queue socket object.

        :return: The queue socket of the sending process.
        """

        return self._queue_socket

    @property
    def socket(self) -> Socket:
        """
        Returns the socket object.

        :return: The socket of sending and receiving data.
        """

        return self.queue_socket.socket

    @property
    def paused(self) -> bool:
        """
        Returns the value of the sending being paused.

        :return: The pause value.
        """

        return self._paused

    @property
    def events(self) -> set[str]:
        """
        Returns the subscribed events.

        :return: The set of event names.
        """

        return self._events.copy()

    @staticmethod
    def subscribe_message(events: Iterable[str]) -> bytes:
        """
        Returns the subscribes message to the given events.

        :param events: The events to subscribe to.

        :return: The bytes stream of the message.
        """

        return Data.encode(Data(name=SUBSCRIBE, time=time.time(), data=list(events)))

    @staticmethod
    def unsubscribe_message(events: Iterable[str]) -> bytes:
        """
        Returns the unsubscribes message to the given events.

        :param events: The events to subscribe to.

        :return: The bytes stream of the message.
        """

        return Data.encode(Data(name=UNSUBSCRIBE, time=time.time(), data=list(events)))

    @staticmethod
    def pause_message() -> bytes:
        """
        Returns the subscribes message to the given events.

        :return: The bytes stream of the message.
        """

        return Data.encode(Data(name=PAUSE, time=time.time()))

    @staticmethod
    def unpause_message() -> bytes:
        """
        Returns the unsubscribes message to the given events.

        :return: The bytes stream of the message.
        """

        return Data.encode(Data(name=UNPAUSE, time=time.time()))

    def subscribe(self, events: Iterable[str]) -> None:
        """
        Subscribes the client to the given events.

        :param events: The events to subscribe to.
        """

        self.queue_socket.send(self.subscribe_message(events=events))

        self._events.update(events)

    def unsubscribe(self, events: Iterable[str]) -> None:
        """
        Unsubscribes the client from the given events.

        :param events: The events to unsubscribe from.
        """

        self.queue_socket.send(self.unsubscribe_message(events=events))

        self._events.difference_update(events)

    def pause(self) -> None:
        """Pauses the data sending process."""

        self.queue_socket.send(self.pause_message())
        
        self._paused = True

    def unpause(self) -> None:
        """Unpauses the data sending process."""

        self.queue_socket.send(self.unpause_message())
        
        self._paused = False

    def data(
            self,
            insert: bool = True,
            load: bool = True
    ) -> Data:
        """
        Receives the data from the socket.

        :param insert: The value to insert the data into the storage.
        :param load: The value to load the data into data objects.

        :return: The data from the server.
        """

        received = self.queue_socket.receive()[0]

        if not received:
            return Data()

        data = Data.decode(received)

        if (
            load and
            (Data.DATA in data) and
            isinstance(data[Data.DATA], dict)
        ):
            data[Data.DATA] = {
                key: Data(**values)
                for key, values in data[Data.DATA].items()
            }

        if (
            insert and
            self.storage and
            (Data.DATA in data) and
            isinstance(data[Data.DATA], dict)
        ):
            self.storage.insert_all(
                (Data(**values) if not isinstance(values, Data) else values)
                for values in data[Data.DATA].values()
            )

        return Data(**data)