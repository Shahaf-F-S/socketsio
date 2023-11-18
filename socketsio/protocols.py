# protocols.py

import socket
from abc import ABCMeta, abstractmethod

from represent import represent

Connection = socket.socket
Address = tuple[str, int]

__all__ = [
    "BufferedProtocol",
    "BaseProtocol",
    "TCP",
    "UDP",
    "BCP",
    "tcp_socket",
    "udp_socket",
    "bluetooth_socket",
    "is_udp",
    "is_tcp",
    "is_tcp_bluetooth",
    "BHP"
]

def tcp_socket() -> Connection:
    """
    Returns a new TCP socket object.

    :return: The socket object.
    """

    return socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# end tcp_socket

def udp_socket() -> Connection:
    """
    Returns a new UDP socket object.

    :return: The socket object.
    """

    return socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# end udp_socket

def bluetooth_socket() -> socket.socket:
    """
    Sends a request through the bluetooth sockets.

    :return: The client object.
    """

    return socket.socket(
        socket.AF_BLUETOOTH, socket.SOCK_STREAM,
        socket.BTPROTO_RFCOMM
    )
# end bluetooth_socket

@represent
class BaseProtocol(metaclass=ABCMeta):
    """Defines the basic parameters for the communication."""

    @staticmethod
    @abstractmethod
    def socket() -> Connection:
        """
        Returns a new base socket object.

        :return: The socket object.
        """
    # end socket

    @abstractmethod
    def send(
            self,
            connection: Connection,
            data: bytes,
            address: Address = None
    ) -> tuple[bytes, Address | None]:
        """
        Sends a message to the client or server by its connection.

        :param data: The message to send to the client.
        :param connection: The sockets' connection object.
        :param address: The address of the sender.
        """
    # end send

    @abstractmethod
    def receive(
            self,
            connection: Connection,
            buffer: int = None,
            address: Address = None
    ) -> tuple[bytes, Address | None]:
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

class TCP(BufferedProtocol):
    """Defines the basic parameters for the communication."""

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
    ) -> tuple[bytes, Address | None]:
        """
        Sends a message to the client or server by its connection.

        :param data: The message to send to the client.
        :param connection: The sockets' connection object.
        :param address: The address of the sender.
        """

        connection.send(data)

        return data, address
    # end send

    def receive(
            self,
            connection: Connection,
            buffer: int = None,
            address: Address = None
    ) -> tuple[bytes, Address | None]:
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
    ) -> tuple[bytes, Address | None]:
        """
        Sends a message to the client or server by its connection.

        :param data: The message to send to the client.
        :param connection: The sockets' connection object.
        :param address: The address of the sender.
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
    ) -> tuple[bytes, Address | None]:
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

class BHP(BaseProtocol):
    """Defines the basic parameters for the communication."""

    HEADER = 32

    def __init__(self, protocol: TCP) -> None:
        """
        Defines the base protocol.

        :param protocol: The base protocol object to use.
        """

        self.protocol = protocol
    # end __init__

    def socket(self) -> Connection:
        """
        Returns a new base socket object.

        :return: The socket object.
        """

        return self.protocol.socket()
    # end socket

    def send(
            self,
            connection: Connection,
            data: bytes,
            address: Address = None
    ) -> tuple[bytes, Address | None]:
        """
        Sends a message to the client or server by its connection.

        :param data: The message to send to the client.
        :param connection: The sockets' connection object.
        :param address: The address of the sender.
        """

        message_len = len(data)

        length_message = (
            ("0" * (self.HEADER - len(str(message_len)))) +
            str(message_len)
        ).encode()

        return self.protocol.send(
            connection=connection, data=length_message + data,
            address=address
        )
    # end send

    def receive(
            self,
            connection: Connection,
            buffer: int = None,
            address: Address = None
    ) -> tuple[bytes, Address | None]:
        """
        Receive a message from the client or server by its connection.

        :param connection: The sockets' connection object.
        :param buffer: The buffer size to collect.
        :param buffer: The length of the message to expect.
        :param address: The address of the sender.

        :return: The received message from the server.
        """

        if buffer is None:
            message, address = self.protocol.receive(
                connection=connection, buffer=self.HEADER, address=address
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
            connection=connection, buffer=buffer, address=address
        )
    # end receive
# end BCP

class BCP(BHP):
    """Defines the basic parameters for the communication."""

    def __init__(self, protocol: TCP, buffer: int = None) -> None:
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
    ) -> tuple[bytes, Address | None]:
        """
        Receive a message from the client or server by its connection.

        :param connection: The sockets' connection object.
        :param buffer: The buffer size to collect.
        :param length: The length of the message to expect.
        :param address: The address of the sender.

        :return: The received message from the server.
        """

        if length is None:
            message, address = self.protocol.receive(
                connection=connection, buffer=self.HEADER, address=address
            )
            length_message = message.decode()

            if not length_message or length_message == '0':
                return b'', address
            # end if

            length = int(length_message)
        # end if

        buffer = buffer or self.buffer

        if buffer >= length:
            return self.protocol.receive(
                connection=connection, buffer=length, address=address
            )
        # end if

        data: list[bytes] = []

        for _ in range(length // buffer):
            payload, address = self.protocol.receive(
                connection=connection, buffer=buffer, address=address
            )

            data.append(payload)
        # end for

        if length % buffer:
            payload, address = self.protocol.receive(
                connection=connection, buffer=length % buffer, address=address
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
    Checks if the socket is a UDP socket.

    :param connection: The socket connection object.

    :return: The boolean flag.
    """

    return is_tcp(connection) and (connection.proto == socket.BTPROTO_RFCOMM)
# end is_tcp_bluetooth