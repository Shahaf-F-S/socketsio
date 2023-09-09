# client.py

import socket

from sockets_communication.client import SocketClient

def main() -> None:
    """Runs the test to test the program."""

    client = SocketClient()
    client.connect(socket.socket(), host="127.0.0.1", port=5000)
    client.send_message_to_server("hello".encode())
    client.send_message_to_server("hello".encode())
# end main

if __name__ == "__main__":
    main()
# end if