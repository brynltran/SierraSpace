import serial
import struct

# Constants
SYNC_PATTERN = b'\x02\x01\x04\x03\x06\x05\x08\x07'
FRAME_HEADER_FORMAT = '<IIIIIIII'  # 
TLV_HEADER_FORMAT = '<II'
DETECTED_OBJ_STRUCT_FORMAT = '<hhhhhh'

class FrameHeader:
    def __init__(self, data):
        unpacked_data = struct.unpack(FRAME_HEADER_FORMAT, data)
        self.version = unpacked_data[0]
        self.total_packet_len = unpacked_data[1]
        self.platform = unpacked_data[2]
        self.frame_number = unpacked_data[3]
        self.time_cpu_cycles = unpacked_data[4]
        self.num_detected_obj = unpacked_data[5]
        self.num_tlvs = unpacked_data[6]
        self.sub_frame_index = unpacked_data[7]

    def __str__(self):
        return f"FrameHeader(version={self.version}, total_packet_len={self.total_packet_len}, platform={self.platform}, frame_number={self.frame_number}, time_cpu_cycles={self.time_cpu_cycles}, num_detected_obj={self.num_detected_obj}, num_tlvs={self.num_tlvs}, sub_frame_index={self.sub_frame_index})"

class DetectedObjectsTLV:
    def __init__(self, data):
        if len(data) < 4:
            print("Error: Not enough data for DetectedObjectsTLV header.")
            return

        self.num_detected_obj, self.xyzQFormat = struct.unpack('<HH', data[:4])
        self.objects = []
        offset = 4

        for _ in range(self.num_detected_obj):
            if offset + 12 > len(data):
                print(f"Error: Not enough data for detected object at offset {offset}.")
                break

            object_data = struct.unpack(DETECTED_OBJ_STRUCT_FORMAT, data[offset:offset + 12])
            self.objects.append({
                'speedIdx': object_data[0],
                'x': object_data[1],
                'y': object_data[2],
                'z': object_data[3],
                'rangeIdx': object_data[4],
                'peakVal': object_data[5]
            })
            offset += 12

def read_frame_header(ser):
    header_size = struct.calcsize(FRAME_HEADER_FORMAT) + len(SYNC_PATTERN)
    data = ser.read(header_size)

    if len(data) != header_size:
        print(f"Error: Expected {header_size} bytes, but received {len(data)} bytes.")
        return None

    if data.startswith(SYNC_PATTERN):
        return FrameHeader(data[len(SYNC_PATTERN):])
    else:
        print("Error: Sync pattern not found in the header data.")
        return None

def read_and_process_tlvs(ser, num_tlvs):
    for _ in range(num_tlvs):
        tlv_header_data = ser.read(struct.calcsize(TLV_HEADER_FORMAT))
        tlv_type, tlv_length = struct.unpack(TLV_HEADER_FORMAT, tlv_header_data)
        tlv_data = ser.read(tlv_length - struct.calcsize(TLV_HEADER_FORMAT))

        if tlv_type == 1:  # Detected Objects TLV
            tlv = DetectedObjectsTLV(tlv_data)
            print(tlv)

def main():
    with serial.Serial('/dev/ttyACM1', 921600) as ser:
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

