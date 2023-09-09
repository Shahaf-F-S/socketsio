# client.py

from socketsio import Client, TCP

def main() -> None:
    """Runs the test to test the program."""

    host = "127.0.0.1"
    port = 5555

    protocol = TCP()

    client = Client(protocol)
    client.connect((host, port))

    for _ in range(2):
        client.send(("hello world" * 1).encode())
        print(client.receive())
    # end for
# end main

if __name__ == "__main__":
    main()
# end if