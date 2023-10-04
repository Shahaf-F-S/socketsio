# protocols.py

import socket
from typing import Optional, Tuple, List
from abc import ABCMeta, abstractmethod

from represent import represent

Connection = socket.socket
Address = Tuple[str, int]

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
    "is_tcp_bluetooth"
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
            address: Optional[Address] = None
    ) -> Tuple[bytes, Optional[Address]]:
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
            buffer: Optional[int] = None,
            address: Optional[Address] = None
    ) -> Tuple[bytes, Optional[Address]]:
        """
        Receive a message from the client or server by its connection.

        :param connection: The sockets' connection object.
        :param buffer: The buffer size to collect.\
        :param address: The address of the sender.

        :return: The received message from the server.
        """
    # end receive
# end BaseProtocol

class BufferedProtocol(BaseProtocol, metaclass=ABCMeta):
    """Defines the basic parameters for the communication."""

    SIZE = 1024

    def __init__(self, size: Optional[int] = None) -> None:
        """
        Defines the attributes of the protocol.

        :param size: The buffer size.
        """

        if size is None:
            size = self.SIZE
        # end if

        self.size = size
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
            address: Optional[Address] = None
    ) -> Tuple[bytes, Optional[Address]]:
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
            buffer: Optional[int] = None,
            address: Optional[Address] = None
    ) -> Tuple[bytes, Optional[Address]]:
        """
        Receive a message from the client or server by its connection.

        :param connection: The sockets' connection object.
        :param buffer: The buffer size to collect.
        :param address: The address of the sender.

        :return: The received message from the server.
        """

        return connection.recv(buffer or self.size), address
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
            address: Optional[Address] = None
    ) -> Tuple[bytes, Optional[Address]]:
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
            buffer: Optional[int] = None,
            address: Optional[Address] = None
    ) -> Tuple[bytes, Optional[Address]]:
        """
        Receive a message from the client or server by its connection.

        :param connection: The sockets' connection object.
        :param buffer: The buffer size to collect.
        :param address: The address of the sender.

        :return: The received message from the server.
        """

        return connection.recvfrom(buffer or self.size)
    # end receive
# end UDP

class BCP(BaseProtocol):
    """Defines the basic parameters for the communication."""

    HEADER = 32

    def __init__(self, protocol: TCP, size: Optional[int] = None) -> None:
        """
        Defines the base protocol.

        :param protocol: The base protocol object to use.
        :param size: The buffer size.
        """

        self.protocol = protocol

        self._size = size
    # end __init__

    @property
    def size(self) -> int:
        """
        Returns the buffer size.

        :return: The buffer size.
        """

        if self._size is None:
            if not isinstance(self.protocol, BufferedProtocol):
                raise ValueError(
                    f"Size is not defined and protocol is "
                    f"not a subclass of {BufferedProtocol}"
                )
            # end if

            return self.protocol.size
        # end if

        return self._size
    # end size

    @size.setter
    def size(self, value: int) -> None:
        """
        Returns the buffer size.

        :param value: The buffer size.
        """

        self._size = value
    # end size

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
            address: Optional[Address] = None
    ) -> Tuple[bytes, Optional[Address]]:
        """
        Sends a message to the client or server by its connection.

        :param data: The message to send to the client.
        :param connection: The sockets' connection object.
        :param address: The address of the sender.
        """

        message_len = len(data)

        size = self.size

        length_message = (
            str(message_len) +
            (" " * (self.HEADER - len(str(message_len))))
        ).encode()

        self.protocol.send(
            connection=connection, data=length_message,
            address=address
        )

        if size >= message_len:
            return self.protocol.send(
                connection=connection, data=data,
                address=address
            )
        # end if

        total = 0

        for i in range(0, message_len, size):
            self.protocol.send(
                connection=connection, data=data[i:i + size],
                address=address
            )

            total += len(data[i:i + size])

            if total == message_len:
                return data, address
            # end if
        # end for

        if message_len % size:
            self.protocol.send(
                connection=connection, data=data[-(message_len % size):],
                address=address
            )
        # end if
    # end send

    def receive(
            self,
            connection: Connection,
            buffer: Optional[int] = None,
            length: Optional[int] = None,
            address: Optional[Address] = None
    ) -> Tuple[bytes, Optional[Address]]:
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

            length = int(length_message[:length_message.find(" ")])
        # end if

        size = buffer or self.size

        if size >= length:
            return self.protocol.receive(
                connection=connection, buffer=length, address=address
            )
        # end if

        data: List[bytes] = []

        for _ in range(length // size):
            payload, address = self.protocol.receive(
                connection=connection, buffer=size, address=address
            )

            data.append(payload)
        # end for

        if length % size:
            payload, address = self.protocol.receive(
                connection=connection, buffer=length % size, address=address
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