import socket
import argparse
import sys

class HelloClient:
    def __init__(self, host="127.0.0.1", port=-1, bufsize=4096):
        self.host = host
        self.port = port
        self.bufsize = bufsize

    def send_and_receive(self, message: str) -> str:
        if self.port == -1:
            print("Error: Port not set. Use --port <number>.")
            sys.exit(1)

        # Empty message is invalid
        assert message != "", "Empty message is not allowed"

        # TODO: Create a socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # TODO: Connect to server
            s.connect((self.host, self.port))
        # TODO: Send message
            s.sendall(message.encode("utf-8"))
        # TODO: Receive reply from server
            reply = s.recv(self.bufsize)
        # TODO: Close socket
            # s.close()
        # TODO: return reply
            return reply.decode("utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Hello Client")
    parser.add_argument("--port", type=int, default=-1, help="Port number to connect to")
    parser.add_argument("--message", type=str, required=True, help="Message to send to server")
    args = parser.parse_args()

    client = HelloClient(port=args.port)
    response = client.send_and_receive(args.message)
    print("Received:", response)
