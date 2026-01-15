import socket
import argparse
import sys

class HelloServer:
    def __init__(self, host="127.0.0.1", port=-1, bufsize=4096):
        self.host = host
        self.port = port
        self.bufsize = bufsize
        self.sock = None

    def start(self):
        if self.port == -1:
            print("Error: Port not set. Use --port <number>.")
            sys.exit(1)

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as self.sock:
            self.sock.bind((self.host, self.port))
            self.sock.listen()
            print(f"Server listening on {self.host} : {self.port}")

            while True:
                conn, addr = self.sock.accept()
                with conn: 
                    print(f"Connected by {addr}")
                    conn.settimeout(2.0)
                    try:
                        data = conn.recv(self.bufsize + 1)
                    except socket.timeout:
                        print("Connection timed out")
                        conn.sendall(b"Empty message")
                        continue

                    if not data:
                        conn.sendall(b"Empty message")
                    elif len(data) > self.bufsize:
                        conn.sendall(b"ERROR: message too long")
                    else: 
                        msg = data.decode("utf-8")
                        response = f"Hello, {msg}"
                        conn.sendall(response.encode("utf-8"))

    def stop(self):
        if self.sock:
            self.sock.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Hello Server")
    parser.add_argument("--port", type=int, default=-1, help="Port number to bind the server on")
    args = parser.parse_args()

    server = HelloServer(port=args.port)
    server.start()
