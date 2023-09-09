# server.py

import socket

from sockets_communication.server import SocketServer

def main() -> None:
    """Runs the test to test the program."""

    server = SocketServer()
    server.connect(socket.socket(), host="127.0.0.1", port=5000)
    server.listen()
# end main

if __name__ == "__main__":
    main()
# end if