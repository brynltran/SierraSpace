import serial
import struct

# Constants
SYNC_PATTERN = b'\x02\x01\x04\x03\x06\x05\x08\x07'
FRAME_HEADER_FORMAT = '<IIIIIIII'  # 
TLV_HEADER_FORMAT = '<II'

# FrameHeader class
class FrameHeader:
    def __init__(self, sync, data):
        values = struct.unpack(FRAME_HEADER_FORMAT, data)
        self.sync = sync
        self.version = values[0]
        self.total_packet_len = values[1]
        self.platform = values[2]
        self.frame_number = values[3]
        self.time_cpu_cycles = values[4]
        self.num_detected_obj = values[5]
        self.num_tlvs = values[6]
        self.sub_frame_index = values[7]

    def __str__(self):
        return (f"FrameHeader(version={self.version}, total_packet_len={self.total_packet_len}, "
                f"platform={self.platform}, frame_number={self.frame_number}, "
                f"time_cpu_cycles={self.time_cpu_cycles}, num_detected_obj={self.num_detected_obj}, "
                f"num_tlvs={self.num_tlvs}, sub_frame_index={self.sub_frame_index})")

# TLV class (example for Detected Objects)
class DetectedObjectsTLV:
    def __init__(self, data):
        self.num_detected_obj, self.xyzQFormat = struct.unpack('<HH', data[:4])
        self.detected_objects = []
        offset = 4
        object_struct_format = '<hhhhhh'
        object_size = struct.calcsize(object_struct_format)

        for _ in range(self.num_detected_obj):
            object_data = struct.unpack(object_struct_format, data[offset:offset + object_size])
            detected_object = {
                'speedIdx': object_data[0],
                'x': object_data[1],
                'y': object_data[2],
                'z': object_data[3],
                'rangeIdx': object_data[4],
                'peakVal': object_data[5]
            }
            self.detected_objects.append(detected_object)
            offset += object_size

    def __str__(self):
        return f"DetectedObjectsTLV(num_detected_obj={self.num_detected_obj}, detected_objects={self.detected_objects})"

# Functions to read and process data from the serial port
def find_sync(ser):
    sync_bytes = b''
    while True:
        byte = ser.read(1)
        if byte:
            sync_bytes = (sync_bytes + byte)[-len(SYNC_PATTERN):]
            if sync_bytes == SYNC_PATTERN:
                return sync_bytes
    return None

def read_frame_header(ser):
    sync = find_sync(ser)
    if sync:
        header_data = ser.read(struct.calcsize(FRAME_HEADER_FORMAT))
        return FrameHeader(sync, header_data)
    return None

def read_and_process_tlvs(ser, num_tlvs):
    tlvs = []
    for _ in range(num_tlvs):
        tlv_header = ser.read(struct.calcsize(TLV_HEADER_FORMAT))
        tlv_type, tlv_length = struct.unpack(TLV_HEADER_FORMAT, tlv_header)
        tlv_data = ser.read(tlv_length - struct.calcsize(TLV_HEADER_FORMAT))

        if tlv_type == 1:  # Detected Objects TLV
            tlv = DetectedObjectsTLV(tlv_data)
            tlvs.append(tlv)

    return tlvs

def main():
    with serial.Serial('/dev/ttyACM1', 921600) as ser:
        print("Serial port opened")
        while True:
            frame_header = read_frame_header(ser)
            if frame_header:
                print(frame_header)
                tlvs = read_and_process_tlvs(ser, frame_header.num_tlvs)
                for tlv in tlvs:
                    print(tlv)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Program terminated by user")
