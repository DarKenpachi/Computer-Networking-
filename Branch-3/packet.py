import struct
import zlib

MAGIC = 0xC0DE 
VER   = 0x01 
TYPE_DATA = 0 
TYPE_ACK  = 1
TYPE_ERR  = 2

# Base header: MAGIC(2) VER(1) TYPE(1) SEQ(4) LEN(2) CHK(4)
_HDR_FMT = "!HBBIHI"
_HDR_SIZE = struct.calcsize(_HDR_FMT)
MAX_PAYLOAD = 1000 # Maximum payload size in bytes

# Last packet adds file checksum (FCHK, 4 bytes)
_HDR_LAST_FMT = "!HBBIHI I"
_HDR_LAST_SIZE = struct.calcsize(_HDR_LAST_FMT)

class Packet:
    @staticmethod
    def checksum(data: bytes) -> int:
        """
        Compute CRC32 checksum (truncate to 32 bits).
        """
        # TODO: implement checksum using zlib.crc32

        # returns a signed integer, so we bitwise AND with 0xFFFFFFFF
        # to ensure it's an unsigned 32-bit integer
        return zlib.crc32(data) & 0xFFFFFFFF

    @staticmethod
    def create(seq: int, data: bytes, pkt_type: int = TYPE_DATA, file_checksum: int = None) -> bytes:
        """
        Build a packet with header + payload.
        - Normal packets: include CHK
        - Last packet: include CHK + FCHK
        """
        # TODO: 1) Ensure payload ≤ MAX_PAYLOAD
        ## chekcks the length of the data to be sent
        length = len(data)
        if length > MAX_PAYLOAD:
            raise ValueError("Payload too large")

        # TODO: 2) Pack header with CHK=0 (and include FCHK if final packet)
        if file_checksum is not None:
            # checksum for last packet
            header = struct.pack(_HDR_LAST_FMT, MAGIC, VER, pkt_type, seq, length, 0, file_checksum) 
        else:
            # Normal packet
            header = struct.pack(_HDR_FMT, MAGIC, VER, pkt_type, seq, length, 0)

        # TODO: 3) Compute checksum over header+payload
        CHK = Packet.checksum(header + data)

        # TODO: 4) Repack header with correct CHK
        if file_checksum is not None:
            # Last packet
            header = struct.pack(_HDR_LAST_FMT, MAGIC, VER, pkt_type, seq, length, CHK, file_checksum)
        else:
            # Normal packet
            header = struct.pack(_HDR_FMT, MAGIC, VER, pkt_type, seq, length, CHK)

        # TODO: 5) Return header+payload
        return header + data

    @staticmethod
    def parse(packet: bytes):
        """
        Parse packet into (pkt_type, seq, data, file_checksum or None).
        Validate MAGIC, VER, LEN, CHK.
        """
        # TODO: 1) Ensure header is long enough. checks if the packet has at least the base header size
        if len(packet) < _HDR_SIZE:
            raise ValueError("Incomplete header")

        # TODO: 2) Unpack base header, validate MAGIC & VER
        base_header = packet[:_HDR_SIZE]
        magic, ver, pkt_type, seq, length, CHK = struct.unpack(_HDR_FMT, base_header)
        if magic != MAGIC:
            raise ValueError("Error in magic")
        if ver != VER:
            raise ValueError("Error in version")

        # TODO: 3) Check payload length matches LEN
        if length > MAX_PAYLOAD:
            raise ValueError("Error in length")

        # determine whether this is a normal or last packet by total size
        if len(packet) == _HDR_SIZE + length:
            is_last = False
        elif len(packet) == _HDR_LAST_SIZE + length:
            is_last = True
        else:
            # Packet size does not match expected header + payload length
            raise ValueError("Error in length")
        
        # TODO: 4) Recompute checksum for a normal packet and compare with CHK
        if not is_last:
            # Extract the payload
            payload = packet[_HDR_SIZE:_HDR_SIZE + length] #extract the payload

            #checksum is recomputed over the header (with CHK=0) + payload
            header_with_zero_chk = struct.pack(_HDR_FMT, magic, ver, pkt_type, seq, length, 0)
            computed_chk = Packet.checksum(header_with_zero_chk + payload)

            # Compare recomputed checksum with the CHK value from the packet
            if computed_chk != CHK:
                raise ValueError("Error in checksum")
            
            ## Return (type, sequence, payload, file_checksum=None)
            return pkt_type, seq, payload, None

        # TODO: 5) Handle last packet with FCHK: unpack last-header, validate,
        # recompute checksum including the FCHK field in the header, and return
        # the file checksum alongside payload.

        #unpack the last packet header
        last_header = packet[:_HDR_LAST_SIZE]
        #unpack all fields include CHK and final file checksum
        magic2, ver2, pkt_type2, seq2, length2, CHK2, file_checksum = struct.unpack(_HDR_LAST_FMT, last_header)

        #Basic checks to ensure base fields didn't change
        if (magic2 != magic) or (ver2 != ver) or (pkt_type2 != pkt_type) or (seq2 != seq) or (length2 != length) or (CHK2 != CHK):
            raise ValueError("Malformed last header")

        #Extract the payload
        payload = packet[_HDR_LAST_SIZE:_HDR_LAST_SIZE + length]

        #Recompute checksum over header (with CHK=0) + payload
        header_with_zero_chk = struct.pack(_HDR_LAST_FMT, magic, ver, pkt_type, seq, length, 0, file_checksum)
        computed_chk = Packet.checksum(header_with_zero_chk + payload)

        #Compare recomputed checksum with the CHK value from the packet
        if computed_chk != CHK:
            raise ValueError("Error in checksum")

        return pkt_type, seq, payload, file_checksum
