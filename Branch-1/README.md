## Steps
1. **Server**
   - Implement `HelloServer.start()`
     - Create a TCP socket
     - Bind it to `(host, port)`
     - Call `listen()`
     - Accept connections in a loop

   - When receiving data:
     - If no data → send back `"Empty message"`
     - If data length > `bufsize` → send back `"ERROR: message too long"`
     - Otherwise → prepend `"Hello, "` and send back

2. **Client**
   - Implement `HelloClient.send_and_receive(message)`
     - Create a TCP socket
     - Connect to the server
     - Send the message
     - Receive the reply
     - Close the socket
     - Return the reply as a string

3. **Command-line arguments**
   - Both client and server must take `--port` argument via `argparse`.
   - Example:
     ```bash
     python server.py --port 5078
     python client.py --port 5078 --message World
     ```
   - Expected output:
     ```
     Received: Hello, World
     ```

---

## Expected Outcome
- Running the server starts a socket listening on the specified port.
- Running the client connects to the server and exchanges messages.
- Program should handle:
  - Normal messages → `"Hello, <msg>"`
  - Empty messages → `"Empty message"`
  - Oversized messages (>4096 bytes) → `"ERROR: message too long"`

---
