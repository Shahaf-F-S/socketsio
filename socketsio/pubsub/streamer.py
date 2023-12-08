# streamer.py

import time
from typing import Callable, Any, Iterable

from looperator import Operator, Handler
from socketsio import SocketSenderQueue, Socket

from socketsio.pubsub.data import Data
from socketsio.pubsub.store import DataStore


__all__ = [
    "RESPONSE",
    "REQUEST",
    "ACTION",
    "Streamer",
    "StreamController",
    "SubscriptionStreamer",
    "ServerSubscriber",
    "SUBSCRIBE",
    "UNPAUSE",
    "UNSUBSCRIBE",
    "PAUSE",
    "DATA",
    "subscribed_stored_data_sender"
]

TIME = "time"

RESPONSE = "response"
REQUEST = "request"

ACTION = "action"


class StreamController:

    MIN_DELAY = 0.00001

    def __init__(
            self,
            socket: Socket | SocketSenderQueue,
            sender: Callable[[], Any] = None,
            receiver: Callable[[], Any] = None,
            termination: Callable[[], Any] = None,
            handler: Handler = None,
            delay: float = None
    ) -> None:

        if not isinstance(socket, SocketSenderQueue):
            queue_socket = SocketSenderQueue(socket)

        else:
            queue_socket = socket

        self._queue_socket = queue_socket
        self._delay = delay

        self.termination = termination

        self.sender = sender
        self.receiver = receiver

        saved_termination = self.queue_socket.termination

        self.queue_socket.termination = lambda: (
            self.socket.close(),
            self.sender.stop(),
            self.receiver.stop(),
            (saved_termination() if saved_termination else None),
            (self.termination if self.termination else ())
        )

        self._handler = handler or Handler()

        saved_callback = handler.exception_callback

        handler.exception_callback = lambda: (
            self.queue_socket.stop(),
            (saved_callback() if saved_callback else None)
        )

        self.queue_socket.handler = handler

        self.sender = Operator(
            handler=handler,
            operation=sender,
            delay=self.delay
        )
        self.receiver = Operator(
            handler=handler,
            operation=receiver,
            delay=self.delay
        )

    @property
    def queue_socket(self) -> SocketSenderQueue:

        return self._queue_socket

    @property
    def socket(self) -> Socket:

        return self.queue_socket.socket

    @property
    def delay(self) -> float:

        return self._delay

    @delay.setter
    def delay(self, value: float) -> None:

        self._delay = max(value, self.MIN_DELAY)

        self.sender.delay = self._delay
        self.receiver.delay = self._delay

    @property
    def handler(self) -> Handler:

        return self._handler

    @handler.setter
    def handler(self, value: Handler) -> None:

        value.exception_callback = self.queue_socket.stop

        self._handler = value

        self.sender.handler = self._handler
        self.receiver.handler = self._handler

    def run(self, send: bool = True, receive: bool = True, block: bool = True) -> None:

        if receive:
            self.receiver.run(block=False)

        if send:
            self.sender.run(block=False)

        self.queue_socket.run(block=block)

    def pause(self) -> None:

        self.sender.pause()
        self.receiver.pause()

    def unpause(self) -> None:

        self.sender.unpause()
        self.receiver.unpause()

    def stop(self) -> None:

        self.receiver.stop()
        self.sender.stop()
        self.queue_socket.stop()

    def close(self) -> None:

        self.queue_socket.close()


Endpoint = Callable[[StreamController, Data], Any]

class Streamer:

    MIN_DELAY = StreamController.MIN_DELAY

    def __init__(
            self,
            sender: Callable[[StreamController], Any] = None,
            receiver: Callable[[StreamController], Any] = None,
            endpoints: dict[str, Endpoint] = None,
            delay: float = None,
            autorun: bool = False
    ) -> None:

        if endpoints is None:
            endpoints = {}

        self._delay = delay or self.MIN_DELAY

        self.autorun = autorun
        self.endpoints = endpoints
        self.sender = sender
        self.receiver = receiver

        self.clients: dict[tuple[str, int], StreamController] = {}

    @property
    def delay(self) -> float:

        return self._delay

    @delay.setter
    def delay(self, value: float) -> None:

        self._delay = max(value, self.MIN_DELAY)

        for controller in self.clients.values():
            controller.delay = value

    def pause(self) -> None:

        for controller in self.clients.values():
            controller.sender.pause()

    def unpause(self) -> None:

        for controller in self.clients.values():
            controller.sender.unpause()

    def block(self) -> None:

        for controller in self.clients.values():
            controller.receiver.pause()

    def unblock(self) -> None:

        for controller in self.clients.values():
            controller.receiver.unpause()

    def stop(self) -> None:

        for controller in self.clients.values():
            controller.stop()

    def send(self, controller: StreamController) -> None:

        if self.sender:
            self.sender(controller)

    def receive(self, controller: StreamController) -> None:

        if self.receiver is not None:
            self.receiver(controller)

            return

        received = controller.socket.receive()[0]

        if not received:
            return

        payload = {}

        try:
            payload = Data.decode(received)
            data = Data.load(payload)

            if data.name not in self.endpoints:
                raise ValueError

            self.endpoints[data.name](controller, data)

        except (ValueError, TypeError, KeyError):
            controller.queue_socket.send(
                Data.encode(
                    Data(
                        name=payload.get(Data.NAME, RESPONSE),
                        time=time.time(),
                        data={
                            RESPONSE: "invalid request",
                            REQUEST: payload
                        }
                    )
                )
            )

    def controller(
            self,
            socket: Socket,
            exception_handler: Callable[[Exception], Any] = None,
            autorun: bool = None,
            send: bool = True,
            receive: bool = True,
            block: bool = True
    ) -> StreamController:

        if autorun is None:
            autorun = self.autorun

        controller = StreamController(
            socket=socket,
            delay=self.delay,
            sender=lambda: self.send(controller),
            receiver=lambda: self.receive(controller),
            handler=Handler(
                exception_handler=exception_handler,
                catch=exception_handler is not None,
                exception_callback=lambda: (
                    self.clients.pop(socket.address, None)
                )
            )
        )

        self.clients[socket.address] = controller

        if autorun:
            controller.run(block=block, send=send, receive=receive)

        return controller

class ServerSubscriber:

    def __init__(
            self,
            controller: StreamController,
            events: Iterable[str] = None
    ) -> None:

        self.controller = controller

        self.events = set(events or ())
        self.data: dict[str, Data] = {}

    def subscribe(self, events: Iterable[str] = None) -> None:

        self.events.update(events or ())

    def unsubscribe(self, events: Iterable[str] = None) -> None:

        self.events.difference_update(events or ())


DATA = "data"
PAUSE = "pause"
UNPAUSE = "unpause"
SUBSCRIBE = "subscribe"
UNSUBSCRIBE = "unsubscribe"

def subscribed_stored_data_sender(
        storage: DataStore,
        socket: Socket,
        subscriber: ServerSubscriber,
        name: str = None
) -> None:

    storage_data = storage.fetch_all(subscriber.events)

    data = {
        key: value.dump() for key, value in storage_data.items()
        if (key not in subscriber.data) or (value.time != subscriber.data[key].time)
    }

    subscriber.data = storage_data

    if data:
        socket.send(Data.encode(Data(name=name or DATA, time=time.time(), data=data)))


class SubscriptionStreamer(Streamer):

    def __init__(
            self,
            subscriber: Callable[[], ServerSubscriber] | type[ServerSubscriber] = None,
            sender: Callable[[StreamController], Any] = None,
            receiver: Callable[[StreamController], Any] = None,
            endpoints: dict[str, Endpoint] = None,
            storage: DataStore = None,
            delay: float = None,
            autorun: bool = False,
            data_name: str = None
    ) -> None:

        if storage is None and sender is None:
            raise ValueError(
                "At least one of 'sender' and 'storage' must be defined, "
                "and 'sender' overrides 'storage'."
            )

        self.subscriber = subscriber or ServerSubscriber
        self.data_name = data_name
        self.subscribers: dict[StreamController, ServerSubscriber] = {}

        super().__init__(
            sender=sender or (
                lambda controller: subscribed_stored_data_sender(
                    storage=storage,
                    socket=controller.queue_socket,
                    subscriber=self.subscribers[controller],
                    name=self.data_name
                )
            ),
            receiver=receiver,
            delay=delay,
            autorun=autorun,
            endpoints={
                PAUSE: lambda controller, _: (
                    controller.sender.pause()
                ),
                UNPAUSE: lambda controller, _: (
                    controller.sender.unpause()
                ),
                SUBSCRIBE: lambda controller, data: (
                    self.subscribers[controller].subscribe(data.data)
                ),
                UNSUBSCRIBE: lambda controller, data: (
                    self.subscribers[controller].unsubscribe(data.data)
                ),
                **(endpoints or {})
            }
        )

        self.storage = storage

    def controller(
            self,
            socket: Socket,
            exception_handler: Callable[[Exception], Any] = None,
            send: bool = True,
            receive: bool = True,
            autorun: bool = None,
            block: bool = True
    ) -> StreamController:

        if autorun is None:
            autorun = self.autorun

        controller = super().controller(
            socket,
            exception_handler=exception_handler,
            block=block
        )

        self.subscribers.setdefault(
            controller,
            self.subscriber(controller=controller)
        )

        if autorun:
            controller.run(block=block, send=send, receive=receive)

        return controller