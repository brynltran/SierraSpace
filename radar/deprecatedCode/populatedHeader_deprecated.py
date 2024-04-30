#!/usr/bin/env python
import serial
import struct
from FrameHeader import FrameHeader
from DetectedObjectsHeader import DetectedObjectsTLV
# Constants
SYNC_PATTERN = b'\x02\x01\x04\x03\x06\x05\x08\x07'
STRUCT_FORMAT = '<IIIIIIII'  # Little endian, sync is 8 bytes but left out | header has 8 bytes unsigned int after 
# Open serial port
ser = serial.Serial('/dev/ttyACM1', 921600)  # baud rate predetermined from Radar  |  ttyACM1 is USB connection

def find_sync(ser):
    sync_bytes = b''
    while True:
        byte = ser.read(1)
        if byte:
            sync_bytes = (sync_bytes + byte)[-len(SYNC_PATTERN):]  # Keep only the last N bytes where N is the length of the SYNC_PATTERN
            if sync_bytes == SYNC_PATTERN:
                return sync_bytes
        else:
            break
    return False

def read_frame_header():
    while True:
        sync = find_sync(ser)
        if sync:
            print("Sync pattern found")
            header_size = struct.calcsize(STRUCT_FORMAT)
            header_data = ser.read(header_size)
            header_class = FrameHeader(sync,header_data)
            print(header_class)
def read_and_process_tlvs(ser, num_tlvs):
    tlvs = []
    for _ in range(num_tlvs):
        tlv_type, tlv_length = struct.unpack('<II', ser.read(8))  # Read the TLV header

        if tlv_type == 1:  # Assuming type 1 is for DetectedObjectsTLV
            data = ser.read(tlv_length - 8)  # Read the rest of the TLV, subtracting the 8 bytes for the header
            tlv = DetectedObjectsTLV(data)
            tlvs.append(tlv)

    return tlvs

if __name__ == "__main__":
    try:
        read_frame_header()
    except KeyboardInterrupt:
        print("Program terminated by user")
    finally:
        ser.close()
        print("Closing Connection")
