import serial
import struct

# Constants
SYNC_PATTERN = b'\x02\x01\x04\x03\x06\x05\x08\x07'
FRAME_HEADER_FORMAT = '<IIIIIIII'  # Adjust the format as necessary
TLV_HEADER_FORMAT = '<II'
DETECTED_OBJ_STRUCT_FORMAT = '<hhhhhh'  # Format for one detected object

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

# TLV class for Detected Objects
class DetectedObjectsTLV:
    def __init__(self, data):
        self.num_detected_obj, self.xyzQFormat = struct.unpack('<HH', data[:4])
        self.objects = []
        offset = 4
        for _ in range(self.num_detected_obj):
            obj_data = data[offset:offset + struct.calcsize(DETECTED_OBJ_STRUCT_FORMAT)]
            if len(obj_data) < struct.calcsize(DETECTED_OBJ_STRUCT_FORMAT):
                print("Error: Not enough data for detected object")
                break
            unpacked_data = struct.unpack(DETECTED_OBJ_STRUCT_FORMAT, obj_data)
            self.objects.append({
                'speedIdx': unpacked_data[0],
                'x': unpacked_data[1],
                'y': unpacked_data[2],
                'z': unpacked_data[3],
                'rangeIdx': unpacked_data[4],
                'peakVal': unpacked_data[5]
            })
            offset += struct.calcsize(DETECTED_OBJ_STRUCT_FORMAT)

    def __str__(self):
        return f"DetectedObjectsTLV(num_detected_obj={self.num_detected_obj}, objects={self.objects})"

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
    for _ in range(num_tlvs):
        tlv_header = ser.read(struct.calcsize(TLV_HEADER_FORMAT))
        tlv_type, tlv_length = struct.unpack(TLV_HEADER_FORMAT, tlv_header)
        tlv_data = ser.read(tlv_length - struct.calcsize(TLV_HEADER_FORMAT))

        if tlv_type == 1:  # Example for Detected Objects TLV
            tlv = DetectedObjectsTLV(tlv_data)
            print(tlv)

def main():
    with serial.Serial('/dev/ttyACM1', 921600) as ser:
        print("Serial port opened")
        while True:
            frame_header = read_frame_header(ser)
            if frame_header:
                print(frame_header)
                read_and_process_tlvs(ser, frame_header.num_tlvs)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Program terminated by user")

