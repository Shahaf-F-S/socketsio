# protocols.py

import socket
from typing import Callable
from abc import ABCMeta, abstractmethod

from represent import represent

__all__ = [
    "BufferedProtocol",
    "BaseProtocol",
    "EmptyProtocol",
    "WrapperProtocol",
    "IdentityWrapperProtocol",
    "TCP",
    "UDP",
    "BCP",
    "BHP",
    "tcp_socket",
    "udp_socket",
    "tcp_bluetooth_socket",
    "is_udp",
    "is_tcp",
    "is_tcp_bluetooth",
    "is_udp_bluetooth",
    "default_protocol",
    "set_default_protocol",
    "reset_default_protocol"
]

Connection = socket.socket
Address = tuple[str, int]
Output = tuple[bytes, Address | None]

def tcp_socket() -> Connection:
    """
    Returns a new TCP socket object.

    :return: The socket object.
    """

    return socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )
# end tcp_socket

def udp_socket() -> Connection:
    """
    Returns a new UDP socket object.

    :return: The socket object.
    """

    return socket.socket(
        socket.AF_INET,
        socket.SOCK_DGRAM
    )
# end udp_socket

def tcp_bluetooth_socket() -> socket.socket:
    """
    Sends a request through the bluetooth sockets.

    :return: The client object.
    """

    return socket.socket(
        socket.AF_BLUETOOTH,
        socket.SOCK_STREAM,
        socket.BTPROTO_RFCOMM
    )
# end tcp_bluetooth_socket

def udp_bluetooth_socket() -> socket.socket:
    """
    Sends a request through the bluetooth sockets.

    :return: The client object.
    """

    return socket.socket(
        socket.AF_BLUETOOTH,
        socket.SOCK_DGRAM,
        socket.BTPROTO_RFCOMM
    )
# end udp_bluetooth_socket

ProtocolConstructor = Callable[[], "BaseProtocol"] | "BaseProtocol"

@represent
class BaseProtocol(metaclass=ABCMeta):
    """Defines the basic parameters for the communication."""

    NAME: str = None
    DEFAULT: ProtocolConstructor = None

    @classmethod
    def protocol(cls) -> "BaseProtocol":
        """
        Returns a protocol object.

        :return: The default protocol object.
        """

        if cls.DEFAULT is None:
            return BHP()
        # end if

        return cls.DEFAULT()
    # end protocol

    @staticmethod
    @abstractmethod
    def socket() -> Connection:
        """
        Returns a new base socket object.

        :return: The socket object.
        """
    # end socket

    def protocols_chain(self) -> list["BaseProtocol"]:
        """
        Returns a chain of protocol objects.

        :return: The list of protocols.
        """

        return [self]
    # end protocols_chain

    def protocol_types_chain(self) -> list[type["BaseProtocol"]]:
        """
        Returns a chain of protocol objects.

        :return: The list of protocols.
        """

        return [type(protocol) for protocol in self.protocols_chain()]
    # end protocol_types_chain

    def is_tcp(self) -> bool:
        """
        Checks if the socket is a TCP socket.

        :return: The boolean flag.
        """

        return isinstance(self, TCP)
    # end is_tcp

    def is_udp(self) -> bool:
        """
        Checks if the socket is a UDP socket.

        :return: The boolean flag.
        """

        return isinstance(self, UDP)
    # end is_udp

    def is_bcp(self) -> bool:
        """
        Checks if the socket is a UDP socket.

        :return: The boolean flag.
        """

        return isinstance(self, BCP)
    # end is_bcp

    def is_bhp(self) -> bool:
        """
        Checks if the socket is a UDP socket.

        :return: The boolean flag.
        """

        return isinstance(self, BHP)
    # end is_bhp

    def is_tcp_based(self) -> bool:
        """
        Checks if the socket is a TCP socket.

        :return: The boolean flag.
        """

        return isinstance(self, TCP)
    # end is_tcp_based

    def is_udp_based(self) -> bool:
        """
        Checks if the socket is a UDP socket.

        :return: The boolean flag.
        """

        return isinstance(self, UDP)
    # end is_udp_based

    def is_bcp_based(self) -> bool:
        """
        Checks if the socket is a UDP socket.

        :return: The boolean flag.
        """

        return isinstance(self, BCP)
    # end is_bcp_based

    def is_bhp_based(self) -> bool:
        """
        Checks if the socket is a UDP socket.

        :return: The boolean flag.
        """

        return isinstance(self, BHP)
    # end is_bhp_based

    def is_wrapper_protocol(self) -> bool:
        """
        Checks if the socket is a UDP socket.

        :return: The boolean flag.
        """

        return isinstance(self, WrapperProtocol)
    # end is_wrapper_protocol

    @abstractmethod
    def send(
            self,
            connection: Connection,
            data: bytes,
            address: Address = None
    ) -> Output:
        """
        Sends a message to the client or server by its connection.

        :param data: The message to send to the client.
        :param connection: The sockets' connection object.
        :param address: The address of the sender.

        :return: The received message from the server.
        """
    # end send

    @abstractmethod
    def receive(
            self,
            connection: Connection,
            buffer: int = None,
            address: Address = None
    ) -> Output:
        """
        Receive a message from the client or server by its connection.

        :param connection: The sockets' connection object.
        :param buffer: The buffer size to collect.
        :param address: The address of the sender.

        :return: The received message from the server.
        """
    # end receive
# end BaseProtocol

class BufferedProtocol(BaseProtocol, metaclass=ABCMeta):
    """Defines the basic parameters for the communication."""

    BUFFER = 1024

    def __init__(self, buffer: int = None) -> None:
        """
        Defines the attributes of the protocol.

        :param buffer: The buffer size.
        """

        if buffer is None:
            buffer = self.BUFFER
        # end if

        self.buffer = buffer
    # end __init__
# end BufferedProtocol

class EmptyProtocol(BaseProtocol, metaclass=ABCMeta):
    """Defines the basic parameters for the communication."""

    def __init__(
            self,
            send: Callable[[Connection, bytes, Address | None], Output],
            receive: Callable[[Connection, int | None, Address | None], Output]
    ) -> None:
        """
        Defines the attributes of the protocol.

        :param send: The function to send data.
        :param receive: The function to received data.
        """

        self._send = send
        self._receive = receive
    # end __init__

    def send(
            self,
            connection: Connection,
            data: bytes,
            address: Address = None
    ) -> Output:
        """
        Sends a message to the client or server by its connection.

        :param data: The message to send to the client.
        :param connection: The sockets' connection object.
        :param address: The address of the sender.

        :return: The received message from the server.
        """

        return self._send(connection, data, address)
    # end send

    def receive(
            self,
            connection: Connection,
            buffer: int = None,
            address: Address = None
    ) -> Output:
        """
        Receive a message from the client or server by its connection.

        :param connection: The sockets' connection object.
        :param buffer: The buffer size to collect.
        :param address: The address of the sender.

        :return: The received message from the server.
        """

        return self._receive(connection, buffer, address)
    # end receive
# end EmptyProtocol

class TCP(BufferedProtocol):
    """Defines the basic parameters for the communication."""

    NAME = "Transmission Control Protocol"

    @staticmethod
    def socket() -> Connection:
        """
        Returns a new base socket object.

        :return: The socket object.
        """

        return tcp_socket()
    # end socket

    def send(
            self,
            connection: Connection,
            data: bytes,
            address: Address = None
    ) -> Output:
        """
        Sends a message to the client or server by its connection.

        :param data: The message to send to the client.
        :param connection: The sockets' connection object.
        :param address: The address of the sender.

        :return: The received message from the server.
        """

        connection.send(data)

        return data, address
    # end send

    def receive(
            self,
            connection: Connection,
            buffer: int = None,
            address: Address = None
    ) -> Output:
        """
        Receive a message from the client or server by its connection.

        :param connection: The sockets' connection object.
        :param buffer: The buffer size to collect.
        :param address: The address of the sender.

        :return: The received message from the server.
        """

        return connection.recv(buffer or self.buffer), address
    # end receive
# end TCP

class UDP(BufferedProtocol):
    """Defines the basic parameters for the communication."""

    NAME = "User Datagram Protocol"

    @staticmethod
    def socket() -> Connection:
        """
        Returns a new base socket object.

        :return: The socket object.
        """

        return udp_socket()
    # end socket

    def send(
            self,
            connection: Connection,
            data: bytes,
            address: Address = None
    ) -> Output:
        """
        Sends a message to the client or server by its connection.

        :param data: The message to send to the client.
        :param connection: The sockets' connection object.
        :param address: The address of the sender.

        :return: The received message from the server.
        """

        if address is None:
            raise ValueError("address must be a tuple of ip and port.")
        # end if

        connection.sendto(data, address)

        return data, address
    # end send

    def receive(
            self,
            connection: Connection,
            buffer: int = None,
            address: Address = None
    ) -> Output:
        """
        Receive a message from the client or server by its connection.

        :param connection: The sockets' connection object.
        :param buffer: The buffer size to collect.
        :param address: The address of the sender.

        :return: The received message from the server.
        """

        return connection.recvfrom(buffer or self.buffer)
    # end receive
# end UDP

class WrapperProtocol(BaseProtocol, metaclass=ABCMeta):
    """Defines the basic parameters for the communication."""

    def __init__(self, protocol: BaseProtocol) -> None:
        """
        Defines the base protocol.

        :param protocol: The base protocol object to use.
        """

        self.protocol = protocol
    # end __init__

    def is_tcp_based(self) -> bool:
        """
        Checks if the socket is a TCP socket.

        :return: The boolean flag.
        """

        return self.protocol.is_tcp_based()
    # end is_tcp_based

    def is_udp_based(self) -> bool:
        """
        Checks if the socket is a UDP socket.

        :return: The boolean flag.
        """

        return self.protocol.is_udp_based()
    # end is_udp_based

    def is_bcp_based(self) -> bool:
        """
        Checks if the socket is a UDP socket.

        :return: The boolean flag.
        """

        return self.is_bcp() or self.protocol.is_bcp_based()
    # end is_bcp_based

    def is_bhp_based(self) -> bool:
        """
        Checks if the socket is a UDP socket.

        :return: The boolean flag.
        """

        return self.is_bhp() or self.protocol.is_bhp_based()
    # end is_bhp_based

    def protocols_chain(self) -> list[BaseProtocol]:
        """
        Returns a chain of protocol objects.

        :return: The list of protocols.
        """

        return [self, *self.protocol.protocols_chain()]
    # end protocols_chain

    def socket(self) -> Connection:
        """
        Returns a new base socket object.

        :return: The socket object.
        """

        return self.protocol.socket()
    # end socket

    @abstractmethod
    def send(
            self,
            connection: Connection,
            data: bytes,
            address: Address = None
    ) -> Output:
        """
        Sends a message to the client or server by its connection.

        :param data: The message to send to the client.
        :param connection: The sockets' connection object.
        :param address: The address of the sender.

        :return: The received message from the server.
        """
    # end send

    @abstractmethod
    def receive(
            self,
            connection: Connection,
            buffer: int = None,
            address: Address = None
    ) -> Output:
        """
        Receive a message from the client or server by its connection.

        :param connection: The sockets' connection object.
        :param buffer: The buffer size to collect.
        :param address: The address of the sender.

        :return: The received message from the server.
        """
    # end receive
# end ProtocolWrapper

class IdentityWrapperProtocol(WrapperProtocol):
    """Defines the basic parameters for the communication."""

    NAME = "Identity Wrapper Protocol"

    def send(
            self,
            connection: Connection,
            data: bytes,
            address: Address = None
    ) -> Output:
        """
        Sends a message to the client or server by its connection.

        :param data: The message to send to the client.
        :param connection: The sockets' connection object.
        :param address: The address of the sender.

        :return: The received message from the server.
        """

        return self.protocol.send(
            connection=connection,
            data=data,
            address=address
        )
    # end send

    def receive(
            self,
            connection: Connection,
            buffer: int = None,
            address: Address = None
    ) -> Output:
        """
        Receive a message from the client or server by its connection.

        :param connection: The sockets' connection object.
        :param buffer: The buffer size to collect.
        :param address: The address of the sender.

        :return: The received message from the server.
        """

        return self.protocol.receive(
            connection=connection,
            buffer=buffer,
            address=address
        )
    # end receive
# end IdentityWrapperProtocol

class BHP(WrapperProtocol):
    """Defines the basic parameters for the communication."""

    NAME = "Buffer Header Protocol"

    HEADER = 32

    def __init__(self, protocol: TCP | WrapperProtocol = None) -> None:
        """
        Defines the base protocol.

        :param protocol: The base protocol object to use.
        """

        super().__init__(protocol=protocol or TCP())
    # end __init__

    def send(
            self,
            connection: Connection,
            data: bytes,
            address: Address = None
    ) -> Output:
        """
        Sends a message to the client or server by its connection.

        :param data: The message to send to the client.
        :param connection: The sockets' connection object.
        :param address: The address of the sender.

        :return: The received message from the server.
        """

        data = str(len(data)).rjust(self.HEADER, "0").encode() + data

        return self.protocol.send(
            connection=connection,
            data=data,
            address=address
        )
    # end send

    def receive(
            self,
            connection: Connection,
            buffer: int = None,
            address: Address = None
    ) -> Output:
        """
        Receive a message from the client or server by its connection.

        :param connection: The sockets' connection object.
        :param buffer: The buffer size to collect.
        :param address: The address of the sender.

        :return: The received message from the server.
        """

        if buffer is None:
            message, address = self.protocol.receive(
                connection=connection,
                buffer=self.HEADER,
                address=address
            )
            length_message = message.decode()

            if (
                not length_message or
                (length_message.count("0") == len(length_message))
            ):
                return b'', address
            # end if

            buffer = int(length_message)
        # end if

        return self.protocol.receive(
            connection=connection,
            buffer=buffer,
            address=address
        )
    # end receive
# end BCP

class BCP(BHP):
    """Defines the basic parameters for the communication."""

    NAME = "Buffer Chunks Protocol"

    def __init__(
            self,
            protocol: TCP | WrapperProtocol = None,
            buffer: int = None
    ) -> None:
        """
        Defines the base protocol.

        :param protocol: The base protocol object to use.
        :param buffer: The buffer size.
        """

        super().__init__(protocol=protocol)

        self._buffer = buffer
    # end __init__

    @property
    def buffer(self) -> int:
        """
        Returns the buffer buffer.

        :return: The buffer buffer.
        """

        if self._buffer is None:
            if not isinstance(self.protocol, BufferedProtocol):
                raise ValueError(
                    f"Size is not defined and protocol is "
                    f"not a subclass of {BufferedProtocol}"
                )
            # end if

            return self.protocol.buffer
        # end if

        return self._buffer
    # end buffer

    @buffer.setter
    def buffer(self, value: int) -> None:
        """
        Returns the buffer buffer.

        :param value: The buffer buffer.
        """

        self._buffer = value
    # end buffer

    def receive(
            self,
            connection: Connection,
            buffer: int = None,
            length: int = None,
            address: Address = None
    ) -> Output:
        """
        Receive a message from the client or server by its connection.

        :param connection: The sockets' connection object.
        :param buffer: The buffer size to collect.
        :param length: The length of the message to expect.
        :param address: The address of the sender.

        :return: The received message from the server.
        """

        if buffer is None:
            message, address = self.protocol.receive(
                connection=connection,
                buffer=self.HEADER,
                address=address
            )
            length_message = message.decode()

            if (
                not length_message or
                (length_message.count("0") == len(length_message))
            ):
                return b'', address
            # end if

            buffer = int(length_message)
        # end if

        buffer = buffer or self.buffer

        if buffer >= length:
            return self.protocol.receive(
                connection=connection,
                buffer=length,
                address=address
            )
        # end if

        data: list[bytes] = []

        for _ in range(length // buffer):
            payload, address = self.protocol.receive(
                connection=connection,
                buffer=buffer,
                address=address
            )

            data.append(payload)
        # end for

        if length % buffer:
            payload, address = self.protocol.receive(
                connection=connection,
                buffer=length % buffer,
                address=address
            )

            data.append(payload)
        # end if

        return b''.join(data), address
    # end receive
# end BCP

def is_tcp(connection: Connection) -> bool:
    """
    Checks if the socket is a TCP socket.

    :param connection: The socket connection object.

    :return: The boolean flag.
    """

    return connection.type == socket.SOCK_STREAM
# end is_tcp

def is_udp(connection: Connection) -> bool:
    """
    Checks if the socket is a UDP socket.

    :param connection: The socket connection object.

    :return: The boolean flag.
    """

    return connection.type == socket.SOCK_DGRAM
# end is_udp

def is_tcp_bluetooth(connection: Connection) -> bool:
    """
    Checks if the socket is a TCP bluetooth socket.

    :param connection: The socket connection object.

    :return: The boolean flag.
    """

    return is_tcp(connection) and (connection.proto == socket.BTPROTO_RFCOMM)
# end is_tcp_bluetooth

def is_udp_bluetooth(connection: Connection) -> bool:
    """
    Checks if the socket is a UDP bluetooth socket.

    :param connection: The socket connection object.

    :return: The boolean flag.
    """

    return is_udp(connection) and (connection.proto == socket.BTPROTO_RFCOMM)
# end is_udp_bluetooth

def default_protocol() -> BaseProtocol:
    """
    Returns a protocol object.

    :return: The default protocol object.
    """

    return BaseProtocol.protocol()
# end default_protocol

def set_default_protocol(constructor: ProtocolConstructor) -> None:
    """
    Sets a new default protocol.

    :param constructor: The default protocol object constructor.
    """

    BaseProtocol.DEFAULT = constructor
# end set_default_protocol

def reset_default_protocol() -> None:
    """Resets protocol object."""

    BaseProtocol.DEFAULT = None
# end reset_default_protocol