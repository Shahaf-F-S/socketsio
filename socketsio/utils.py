# utils.py

import socket
import errno

__all__ = [
    "find_available_port",
    "is_used_port"
]

def find_available_port(host: str) -> int:
    """
    Finds an available port for the host.

    :param host: The host to connect a port with.

    :return: The found port.
    """

    sock = socket.socket()
    sock.bind((host, 0))

    return sock.getsockname()[1]
# end find_available_port

def is_used_port(host: str, port: int) -> bool:
    """
    Checks if a port is already used.

    :param host: The host.
    :param port: The port.

    :return: The boolean flag.
    """

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind((host, port))

        except socket.error as e:
            if e.errno == errno.EADDRINUSE:
                return True

            else:
                raise e
            # end if
        # end try
    # end socket

    return False
# end is_used_port