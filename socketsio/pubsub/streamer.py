# streamer.py

import time
from typing import Callable, Any, Iterable
from dataclasses import dataclass

from represent import represent

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
    "subscribed_stored_data_sender",
    "Authorization",
    "AUTHENTICATE"
]

TIME = "time"

RESPONSE = "response"
REQUEST = "request"

ACTION = "action"


class StreamController:
    """An object to control the stream of data from and to a client."""

    MIN_DELAY = 0.00001

    def __init__(
            self,
            socket: Socket | SocketSenderQueue,
            sender: Callable[[], Any] = None,
            receiver: Callable[[], Any] = None,
            termination: Callable[[], Any] = None,
            handler: Handler = None,
            delay: float = None,
            authenticated: bool = True
    ) -> None:
        """
        Defines the attributes of the object.

        :param socket: The socket object.
        :param sender: The sender callback.
        :param receiver: The receiver callback.
        :param termination: The termination callback.
        :param handler: The handler object.
        :param delay: The delay value.
        :param authenticated: The value of authentication.
        """

        if not isinstance(socket, SocketSenderQueue):
            queue_socket = SocketSenderQueue(socket)

        else:
            queue_socket = socket

        self._queue_socket = queue_socket
        self._delay = delay

        self.authenticated = authenticated
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
    def delay(self) -> float:
        """
        Returns the delay value.

        :return: The delay in seconds.
        """

        return self._delay

    @delay.setter
    def delay(self, value: float) -> None:
        """
        Sets the delay value.

        :param value: The delay in seconds.
        """

        self._delay = max(value, self.MIN_DELAY)

        self.sender.delay = self._delay
        self.receiver.delay = self._delay

    @property
    def handler(self) -> Handler:
        """
        Returns the handler object.

        :return: The handler of all processes in the controller.
        """

        return self._handler

    @handler.setter
    def handler(self, value: Handler) -> None:
        """
        Sets the handler object.

        :param value: The new handler of all processes in the controller.
        """

        value.exception_callback = self.queue_socket.stop

        self._handler = value

        self.sender.handler = self._handler
        self.receiver.handler = self._handler

    def run(self, send: bool = True, receive: bool = True, block: bool = True) -> None:
        """
        Runs the controller for sending and receiving data.

        :param send: The value to run the data sending process.
        :param receive: The value to run the data receiving process.
        :param block: The value to block the thread.
        """

        if receive:
            self.receiver.run(block=False)

        if send:
            self.sender.run(block=False)

        self.queue_socket.run(block=block)

    def pause(self) -> None:
        """Pauses all processes of the controller."""

        self.sender.pause()
        self.receiver.pause()
        self.queue_socket.pause()

    def unpause(self) -> None:
        """Unpauses all processes of the controller."""

        self.queue_socket.unpause()
        self.sender.unpause()
        self.receiver.unpause()

    def stop(self) -> None:
        """Stops all processes of the controller."""

        self.receiver.stop()
        self.sender.stop()
        self.queue_socket.stop()

    def close(self) -> None:
        """Stops and closes communication."""

        self.stop()
        self.queue_socket.close()

@represent
@dataclass(repr=False)
class Authorization:
    """A class to represent an authorization object."""

    authorized: bool
    response: str = None


Endpoint = Callable[[StreamController, Data], Any]

class Streamer:
    """A class to represent an endpoints based stream producer and handler."""

    MIN_DELAY = StreamController.MIN_DELAY

    def __init__(
            self,
            sender: Callable[[StreamController], Any] = None,
            receiver: Callable[[StreamController], Any] = None,
            authenticate: Callable[[Data], Authorization] = None,
            constructor: Callable[[], StreamController] | type[StreamController] = None,
            endpoints: dict[str, Endpoint] = None,
            delay: float = None,
            autorun: bool = False
    ) -> None:
        """
        Defines the attributes of the object.

        :param sender: The data sending handler.
        :param receiver: The data receiving handler.
        :param authenticate: The authentication handler.
        :param endpoints: The communication endpoints.
        :param constructor: The controller constructor.
        :param delay: The delay value for the controllers.
        :param autorun: The value to run controllers on creation.
        :param authenticate: The value to authenticate clients.
        """

        if endpoints is None:
            endpoints = {}

        self._delay = delay or self.MIN_DELAY

        self.autorun = autorun
        self.endpoints = endpoints
        self.sender = sender
        self.receiver = receiver
        self.constructor = constructor or StreamController
        self.authenticate = authenticate or (lambda: Authorization(True))

        if self.authenticate and AUTHENTICATE not in self.endpoints:
            self.endpoints[AUTHENTICATE] = self.authentication

        self.clients: dict[tuple[str, int], StreamController] = {}

    @property
    def delay(self) -> float:
        """
        Returns the delay value.

        :return: The delay in seconds.
        """

        return self._delay

    @delay.setter
    def delay(self, value: float) -> None:
        """
        Sets the delay value.

        :param value: The delay in seconds.
        """

        self._delay = max(value, self.MIN_DELAY)

        for controller in self.clients.values():
            controller.delay = value

    def pause(self) -> None:
        """Pauses all controllers of the streamer."""

        for controller in self.clients.values():
            controller.sender.pause()

    def unpause(self) -> None:
        """Unpauses all controllers of the streamer."""

        for controller in self.clients.values():
            controller.sender.unpause()

    def block(self) -> None:
        """Blocks all controllers of the streamer."""

        for controller in self.clients.values():
            controller.receiver.pause()

    def unblock(self) -> None:
        """Unblocks all controllers of the streamer."""

        for controller in self.clients.values():
            controller.receiver.unpause()

    def stop(self) -> None:
        """Stops all controllers of the streamer."""

        for controller in self.clients.values():
            controller.stop()

    def close(self) -> None:
        """Stops and closes all controllers of the streamer."""

        for controller in self.clients.values():
            controller.close()

    def send(self, controller: StreamController) -> None:
        """
        Runs the sending handler.

        :param controller: The controller to pass to the handler.
        """

        if self.authenticate and not controller.authenticated:
            return

        if self.sender:
            self.sender(controller)

    def authentication(self, controller: StreamController, data: Data) -> None:

        authorization = self.authenticate(data)

        if not authorization.authorized:
            response = (
                authorization.response or
                "invalid authentication"
            )

        else:
            response = (
                authorization.response or
                "authorized"
            )

        controller.authenticated = authorization.authorized

        controller.queue_socket.send(
            Data.encode(
                Data(
                    name=data.name,
                    time=time.time(),
                    data={
                        RESPONSE: response,
                        REQUEST: data.dump()
                    }
                )
            )
        )

    def receive(self, controller: StreamController) -> None:
        """
        Runs the receiving handler.

        :param controller: The controller to pass to the handler.
        """

        if self.receiver is not None:
            self.receiver(controller)

            return

        received = controller.socket.receive()[0]

        if not received:
            return

        payload = {}

        response = "invalid request"

        try:
            payload = Data.decode(received)
            data = Data.load(payload)

            if (
                self.authenticate and
                (data.name != AUTHENTICATE) and
                (not controller.authenticated)
            ):
                response = "unauthenticated"

                raise ValueError

            self.endpoints[data.name](controller, data)

        except (ValueError, TypeError, KeyError):
            controller.queue_socket.send(
                Data.encode(
                    Data(
                        name=payload.get(Data.NAME, RESPONSE),
                        time=time.time(),
                        data={
                            RESPONSE: response,
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
        """
        Creates and returns a controller object.

        :param socket: The socket for the controller.
        :param exception_handler: The exception handler for the handler of the controller.
        :param autorun: The value to run the controller.
        :param send: The value to run the sending process of the controller.
        :param receive: The value to run the receiving process of the controller.
        :param block: The value to block the thread on run.

        :return: The controller object.
        """

        if autorun is None:
            autorun = self.autorun

        controller = (self.constructor or StreamController)(
            socket=socket,
            delay=self.delay,
            authenticated=self.authenticate is None,
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
    """A class to represent a server-side subscriber."""

    def __init__(
            self,
            controller: StreamController,
            events: Iterable[str] = None
    ) -> None:
        """
        Defines the attributes of the object.

        :param controller: The controller object to control the processes of the client.
        :param events: The events the client is already subscribed to.
        """

        self.controller = controller

        self.events = set(events or ())
        self.data: dict[str, Data] = {}

    def subscribe(self, events: Iterable[str] = None) -> None:
        """
        Subscribes the client to the given events.

        :param events: The events to subscribe to.
        """

        self.events.update(events or ())

    def unsubscribe(self, events: Iterable[str] = None) -> None:
        """
        Unsubscribes the client from the given events.

        :param events: The events to unsubscribe from.
        """

        self.events.difference_update(events or ())


DATA = "data"
PAUSE = "pause"
UNPAUSE = "unpause"
SUBSCRIBE = "subscribe"
UNSUBSCRIBE = "unsubscribe"
AUTHENTICATE = "authenticate"

def subscribed_stored_data_sender(
        storage: DataStore,
        socket: Socket,
        subscriber: ServerSubscriber,
        name: str = None
) -> None:
    """
    Sends the storage data by the subscriptions of the subscriber.

    :param storage: The data storage object.
    :param socket: The socket object for sending data.
    :param subscriber: The subscriber object.
    :param name: The name of the data to send
    """

    storage_data = storage.fetch_all(subscriber.events)

    data = {
        key: value.dump() for key, value in storage_data.items()
        if (key not in subscriber.data) or (value.time != subscriber.data[key].time)
    }

    subscriber.data = storage_data

    if data:
        socket.send(Data.encode(Data(name=name or DATA, time=time.time(), data=data)))


class SubscriptionStreamer(Streamer):
    """A class to represent a subscription based stream producer and handler."""

    def __init__(
            self,
            subscriber: Callable[[], ServerSubscriber] | type[ServerSubscriber] = None,
            sender: Callable[[StreamController], Any] = None,
            receiver: Callable[[StreamController], Any] = None,
            authenticate: Callable[[Data], Authorization] = None,
            constructor: Callable[[], StreamController] | type[StreamController] = None,
            endpoints: dict[str, Endpoint] = None,
            storage: DataStore = None,
            delay: float = None,
            autorun: bool = False,
            data_name: str = None
    ) -> None:
        """
        Defines the attributes of the object.

        :param sender: The data sending handler.
        :param receiver: The data receiving handler.
        :param authenticate: The authentication handler.
        :param endpoints: The communication endpoints.
        :param delay: The delay value for the controllers.
        :param autorun: The value to run controllers on creation.
        :param subscriber: The subscriber base class.
        :param storage: The storage object.
        :param data_name: The data name.
        """

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
            constructor=constructor,
            authenticate=authenticate,
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
        """
        Creates and returns a controller object.

        :param socket: The socket for the controller.
        :param exception_handler: The exception handler for the handler of the controller.
        :param autorun: The value to run the controller.
        :param send: The value to run the sending process of the controller.
        :param receive: The value to run the receiving process of the controller.
        :param block: The value to block the thread on run.

        :return: The controller object.
        """

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