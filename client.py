# client.py

from socketsio import Client, BHP, TCP, UDP

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

    for _ in range(2):
        client.send((", ".join(["hello world"] * 3)).encode())
        print("client:", client.receive())

if __name__ == '__main__':
    main()
