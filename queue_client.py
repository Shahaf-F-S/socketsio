# client.py

from socketsio import Client, BCP, TCP, UDP, SocketSenderQueue

HOST = "127.0.0.1"
PROTOCOL = 'TCP'
PORT = 5000

def main() -> None:
    """Tests the program."""

    if PROTOCOL == 'UDP':
        protocol = UDP()

    elif PROTOCOL == 'TCP':
        protocol = BCP(TCP())

    else:
        raise ValueError(f"Invalid protocol type: {PROTOCOL}")
    # end if

    client = Client(protocol)
    client.connect((HOST, PORT))

    queue = SocketSenderQueue(client)

    for _ in range(2):
        queue.send((", ".join(["hello world"] * 3)).encode())
    # end for

    queue.send_all_queue()

    for _ in range(2):
        print("client:", queue.receive())
    # end for
# end main

if __name__ == '__main__':
    main()
# end if