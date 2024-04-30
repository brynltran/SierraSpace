import serial
import struct
import matplotlib.pyplot as plt

# Assuming the rest of your classes and functions are defined above...

def plot_detected_objects(objects):
    x_coords = [obj['x'] for obj in objects]
    y_coords = [obj['y'] for obj in objects]

    plt.scatter(x_coords, y_coords)
    plt.xlabel('X Coordinate')
    plt.ylabel('Y Coordinate')
    plt.title('Detected Objects')
    plt.grid(True)
    plt.show()

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
        # Assuming the first 4 bytes indicate the number of detected objects and xyzQFormat
        header_format = '<HH'  # Two shorts for num_detected_obj and xyzQFormat
        header_size = struct.calcsize(header_format)
        if len(data) >= header_size:
            self.num_detected_obj, self.xyzQFormat = struct.unpack(header_format, data[:header_size])
            self.objects = []

            offset = header_size
            object_struct_format = '<hhhhhh'  # Format for each object
            object_size = struct.calcsize(object_struct_format)

            for _ in range(self.num_detected_obj):
                if offset + object_size <= len(data):
                    object_data = struct.unpack(object_struct_format, data[offset:offset + object_size])
                    self.objects.append({
                        'speedIdx': object_data[0],
                        'x': object_data[1],
                        'y': object_data[2],
                        'z': object_data[3],
                        'rangeIdx': object_data[4],
                        'peakVal': object_data[5]
                    })
                    offset += object_size
                else:
                    print(f"Error: Not enough data for detected object at offset {offset}.")
                    break
        else:
            print("Error: Not enough data for DetectedObjectsTLV header.")
            self.num_detected_obj = 0
            self.objects = []

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
    tlvs = []
    for _ in range(num_tlvs):
        tlv_header_data = ser.read(struct.calcsize(TLV_HEADER_FORMAT))
        if len(tlv_header_data) < struct.calcsize(TLV_HEADER_FORMAT):
            print("Error: TLV header data is too short.")
            continue

        tlv_type, tlv_length = struct.unpack(TLV_HEADER_FORMAT, tlv_header_data)
        if tlv_length > struct.calcsize(TLV_HEADER_FORMAT):
            tlv_data = ser.read(tlv_length - struct.calcsize(TLV_HEADER_FORMAT))
            if tlv_type == 1:  # Example for Detected Objects TLV
                if len(tlv_data) >= (tlv_length - struct.calcsize(TLV_HEADER_FORMAT)):
                    tlv = DetectedObjectsTLV(tlv_data)
                    tlvs.append(tlv)
                else:
                    print("Error: Not enough data for TLV content.")
        else:
            print("Error: TLV length is too short for its content.")
    return tlvs
def plot_detected_objects(objects):
    x_coords = [obj['x'] for obj in objects]
    y_coords = [obj['y'] for obj in objects]

    plt.scatter(x_coords, y_coords)
    plt.xlabel('X Coordinate')
    plt.ylabel('Y Coordinate')
    plt.title('Detected Objects')
    plt.show()

def main():
    with serial.Serial('/dev/ttyACM1', 921600) as ser:
        print("Serial port opened")
        while True:
            frame_header = read_frame_header(ser)
            if frame_header:
                print(frame_header)
                tlvs = read_and_process_tlvs(ser, frame_header.num_tlvs)
                for tlv in tlvs:
                    if isinstance(tlv, DetectedObjectsTLV):
                        plot_detected_objects(tlv.objects)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Program terminated by user")
