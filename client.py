# test.py

from socketsio import Client, UDP, BCP, TCP

HOST = "127.0.0.1"
PROTOCOL = 'UDP'
PORT = 5000

def main() -> None:
    """Tests the program."""

    if PROTOCOL == 'UDP':
        protocol = BCP(UDP())

    elif PROTOCOL == 'TCP':
        protocol = BCP(TCP())

    else:
        raise ValueError(f"Invalid protocol type: {PROTOCOL}")
    # end if

    client = Client(protocol)
    client.connect((HOST, PORT))

    for _ in range(2):
        client.send(("hello world" * 1).encode())
        print(client.receive())
    # end for
# end main

if __name__ == '__main__':
    main()
# end if