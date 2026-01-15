## Objective

Build a class-based client/server that exchanges large data (~1 MB) over UDP using a custom binary packet.  
Students will implement packet creation and decoding with:

* A fixed header: `MAGIC (2B) | VER (1B) | TYPE (1B) | SEQ (4B) | LEN (2B) | CHK (4B)`  
* An optional file checksum (FCHK, 4B) in the last packet only.  
* Payload length in the header.  
* Header checksum computed over `(header with CHK=0, FCHK unchanged) + payload`.  
* File checksum computed over the entire dataset and carried only in the last packet.

Most of the work is in `packet.py` (skeleton provided). `client.py` and `server.py` are intentionally simple so they “just work” once the packet layer is correct.

---

# Packet Header Format

The header is 14 bytes for normal packets, and 18 bytes for the last packet.

```

| Field | Size (bytes) | Description                                    |
| ----- | ------------ | ---------------------------------------------- |
| MAGIC | 2            | Fixed constant `0xC0DE`                        |
| VER   | 1            | Protocol version (currently 0x01)              |
| TYPE  | 1            | Packet type (DATA=0, ACK=1, ERR=2)             |
| SEQ   | 4            | Sequence number of this packet                 |
| LEN   | 2            | Payload length in bytes (≤1000)                |
| CHK   | 4            | CRC32 of header (with CHK=0) + payload         |
| FCHK  | 4 (optional) | CRC32 of the entire file, only in the last pkt |

```

---

### Visual Layout

```

Normal packet (14-byte header):

0      1      2      3      4      5      6      7      8     ...   13
+------+------+------+------+------+------+------+------+------+------+
\|   MAGIC (0xC0DE)   | VER  | TYPE |             SEQ              |
+------+------+------+------+------+------+------+------+------+------+
\|        LEN         |              CHK (32 bits)                 |
+------+------+------+------+------+------+------+------+------+------+
\|              PAYLOAD (LEN bytes) ...
+---------------------------------------------------------------+

Final packet (18-byte header):

0 ... 13 same as above, plus:
14     15     16     17
+------+------+------+------+
\|        FCHK (32 bits)     |
+------+------+------+------+
\|              PAYLOAD (LEN bytes) ...
+---------------------------------------------------------------+

````

- MAGIC helps detect invalid packets.  
- VER allows future protocol updates.  
- TYPE distinguishes DATA, ACK, and ERR.  
- SEQ orders packets (0, 1, 2, …).  
- LEN is the payload size.  
- CHK validates each packet.  
- FCHK validates the full file at the end.  

---

## Steps

### 1) Implement the Packet Layer (students)

Open `packet.py` and complete:

* `checksum(data: bytes) -> int`
* `create(seq: int, data: bytes, pkt_type: int, file_checksum: int=None) -> bytes`
* `parse(packet: bytes) -> tuple[int, int, bytes, int|None]`

Protocol constants you’ll use:

```python
MAGIC = 0xC0DE
VER   = 0x01
TYPE_DATA = 0
TYPE_ACK  = 1
TYPE_ERR  = 2
_HDR_FMT       = "!HBBIHI"   # normal
_HDR_LAST_FMT  = "!HBBIHI I" # last packet with file checksum
MAX_PAYLOAD    = 1000
````

Guidelines:

* Split the 1 MB file into 1000-byte chunks.
* Each packet gets an incrementing SEQ number.
* Final packet carries the file checksum (CRC32 of the whole file).
* Server reassembles data by sequence order and validates against FCHK.

---

### 2) Run the server

```bash
python3 server.py --port 6000
```

Expected:

```
Server listening on 127.0.0.1:6000
```

### 3) Run the client

```bash
python3 client.py --port 6000 --file test.bin
```

Expected:

```
Transfer complete.
```
You can create the test.bin file using either ``dd" or ``fallocate" commands.
You can also use any other file.

---

## Expected Outcome

* `Packet.create` produces correct headers and payloads.
* `Packet.parse` validates and extracts fields.
* Server reassembles the file correctly.
* Server detects missing or corrupted packets.
* Server verifies file checksum from the last packet.
* Client prints confirmation when the transfer is done.

---
