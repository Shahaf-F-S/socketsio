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
    "base_socket",
    "tcp_socket",
    "udp_socket",
    "bluetooth_socket"
]

def base_socket() -> Connection:
    """
    Returns a new base socket object.

    :return: The socket object.
    """

    return socket.socket()
# end base_socket

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
        socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM
    )
# end bluetooth_socket

@represent
class BaseProtocol(metaclass=ABCMeta):
    """Defines the basic parameters for the communication."""

    @staticmethod
    def socket() -> Connection:
        """
        Returns a new base socket object.

        :return: The socket object.
        """

        return base_socket()
    # end socket

    @abstractmethod
    def send(
            self,
            connection: Connection,
            data: bytes,
            address: Optional[Address] = None
    ) -> None:
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
            address: Optional[Address] = None,
            buffer: Optional[int] = None
    ) -> bytes:
        """
        Receive a message from the client or server by its connection.

        :param connection: The sockets' connection object.
        :param address: The address of the sender.
        :param buffer: The buffer size to collect.

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

    def send(
            self,
            connection: Connection,
            data: bytes,
            address: Optional[Address] = None
    ) -> None:
        """
        Sends a message to the client or server by its connection.

        :param data: The message to send to the client.
        :param connection: The sockets' connection object.
        :param address: The address of the sender.
        """

        connection.send(data)
    # end send

    def receive(
            self,
            connection: Connection,
            address: Optional[Address] = None,
            buffer: Optional[int] = None
    ) -> bytes:
        """
        Receive a message from the client or server by its connection.

        :param connection: The sockets' connection object.
        :param address: The address of the sender.
        :param buffer: The buffer size to collect.

        :return: The received message from the server.
        """

        return connection.recv(buffer or self.size)
    # end receive
# end TCP

class UDP(BufferedProtocol):
    """Defines the basic parameters for the communication."""

    def send(
            self,
            connection: Connection,
            data: bytes,
            address: Optional[Address] = None
    ) -> None:
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
    # end send

    def receive(
            self,
            connection: Connection,
            address: Optional[Address] = None,
            buffer: Optional[int] = None
    ) -> bytes:
        """
        Receive a message from the client or server by its connection.

        :param connection: The sockets' connection object.
        :param address: The address of the sender.
        :param buffer: The buffer size to collect.

        :return: The received message from the server.
        """

        if address is None:
            raise ValueError("address must be a tuple of ip and port.")
        # end if

        return connection.recvfrom(buffer or self.size)[0]
    # end receive
# end UDP

class BCP(BaseProtocol):
    """Defines the basic parameters for the communication."""

    HEADER = 32

    def __init__(self, protocol: BufferedProtocol) -> None:
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
            address: Optional[Address] = None
    ) -> None:
        """
        Sends a message to the client or server by its connection.

        :param data: The message to send to the client.
        :param connection: The sockets' connection object.
        :param address: The address of the sender.
        """

        message_len = len(data)

        size = self.protocol.size

        length_message = (
            str(message_len) +
            (" " * (self.HEADER - len(str(message_len))))
        ).encode()

        self.protocol.send(
            connection=connection,
            data=length_message,
            address=address
        )

        if size >= message_len:
            return self.protocol.send(
                connection=connection,
                data=data,
                address=address
            )
        # end if

        for i in range(0, message_len, size):
            self.protocol.send(
                connection=connection,
                data=data[i:i + size],
                address=address
            )
        # end for

        if message_len % size:
            self.protocol.send(
                connection=connection,
                data=data[-(message_len % size):],
                address=address
            )
        # end if
    # end send

    def receive(
            self,
            connection: Connection,
            address: Optional[Address] = None,
            buffer: Optional[int] = None
    ) -> bytes:
        """
        Receive a message from the client or server by its connection.

        :param connection: The sockets' connection object.
        :param address: The address of the sender.
        :param buffer: The buffer size to collect.

        :return: The received message from the server.
        """

        length_message = self.protocol.receive(
            connection=connection,
            address=address,
            buffer=self.HEADER
        ).decode()

        if not length_message or length_message == '0':
            return b''
        # end if

        message_len = int(length_message[:length_message.find(" ")])

        size = buffer or self.protocol.size

        if size >= message_len:
            return self.protocol.receive(
                connection=connection,
                address=address,
                buffer=message_len
            )
        # end if

        data: List[bytes] = []

        for _ in range(message_len // size):
            data.append(
                self.protocol.receive(
                    connection=connection,
                    address=address,
                    buffer=size
                )
            )
        # end for

        if message_len % size:
            data.append(
                self.protocol.receive(
                    connection=connection,
                    address=address,
                    buffer=message_len % size
                )
            )
        # end if

        return b''.join(data)
    # end receive
# end BCP