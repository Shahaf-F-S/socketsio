# client.py

from socketsio import Client, BHP, TCP, UDP, SocketSenderQueue

HOST = "127.0.0.1"
PROTOCOL = 'TCP'
PORT = 5000

def main() -> None:
    """Tests the program."""

    if PROTOCOL == 'UDP':
        protocol = UDP()

    elif PROTOCOL == 'TCP':
        protocol = BHP(TCP())

    else:
        raise ValueError(f"Invalid protocol type: {PROTOCOL}")

    client = Client(protocol)
    client.connect((HOST, PORT))

    queue = SocketSenderQueue(client)

    for _ in range(2):
        queue.send((", ".join(["hello world"] * 3)).encode())

    queue.send_all_queue()

    for _ in range(2):
        print("client:", queue.receive())

if __name__ == '__main__':
    main()
