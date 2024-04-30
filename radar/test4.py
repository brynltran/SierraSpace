import serial
import struct
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Constants
SYNC_PATTERN = b'\x02\x01\x04\x03\x06\x05\x08\x07'
FRAME_HEADER_FORMAT = '<IIIIIIII'  # Adjust the format as necessary
TLV_HEADER_FORMAT = '<II'
OBJECT_STRUCT_FORMAT = '<hhhhhh'

# Initialize plot
fig, ax = plt.subplots()
sc = ax.scatter([], [])
xdata, ydata = [], []

class FrameHeader:
    def __init__(self, data):
        values = struct.unpack(FRAME_HEADER_FORMAT, data)
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

class DetectedObjectsTLV:
    def __init__(self, data):
        if len(data) < 4:
            print("Error: Not enough data for DetectedObjectsTLV header.")
            return

        self.num_detected_obj, self.xyzQFormat = struct.unpack('<HH', data[:4])

        self.objects = []
        offset = 4
        object_struct_format = '<hhhhhh'
        object_size = struct.calcsize(object_struct_format)

        for _ in range(self.num_detected_obj):
            if offset + object_size > len(data):
                print(f"Error: Not enough data for detected object at offset {offset}.")
                break  # Not enough data, break out of the loop

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
        # Read the remaining part of the header after the sync pattern
        remaining_header_size = struct.calcsize(FRAME_HEADER_FORMAT) - len(SYNC_PATTERN)
        header_data = ser.read(remaining_header_size)
        full_header_data = sync + header_data  # Combine sync and the rest of the header
        if len(full_header_data) == struct.calcsize(FRAME_HEADER_FORMAT):
            return FrameHeader(full_header_data)
        else:
            print("Error: Incomplete frame header received.")
    return None

def update_plot(frame, ser):
    frame_header = read_frame_header(ser)
    if frame_header:
        print(frame_header)
        num_tlvs = frame_header.num_tlvs
        for _ in range(num_tlvs):
            tlv_header = ser.read(struct.calcsize(TLV_HEADER_FORMAT))
            tlv_type, tlv_length = struct.unpack(TLV_HEADER_FORMAT, tlv_header)
            tlv_data = ser.read(tlv_length - struct.calcsize(TLV_HEADER_FORMAT))

            if tlv_type == 1:  # Detected Objects TLV
                tlv = DetectedObjectsTLV(tlv_data)
                print(tlv)
                xdata = [obj['x'] for obj in tlv.objects]
                ydata = [obj['y'] for obj in tlv.objects]
                sc.set_offsets(list(zip(xdata, ydata)))

def main():
    with serial.Serial('/dev/ttyACM1', 921600) as ser:
        print("Serial port opened")
        ani = FuncAnimation(fig, update_plot, fargs=(ser,), interval=100)
        plt.show()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Program terminated by user")
        plt.close('all')

