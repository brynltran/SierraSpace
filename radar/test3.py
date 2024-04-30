import serial
import struct
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation


# Constants
# Constants
SYNC_PATTERN = b'\x02\x01\x04\x03\x06\x05\x08\x07'
FRAME_HEADER_FORMAT = '<IIIIIIII'  # Adjust the format as necessary
TLV_HEADER_FORMAT = '<II'  # Type and Length for TLV header

class FrameHeader:
    def __init__(self, data):
        # Assuming data starts immediately after the sync pattern
        values = struct.unpack(FRAME_HEADER_FORMAT, data)
        self.version = values[0]
        self.total_packet_len = values[1]
        self.platform = values[2]
        self.frame_number = values[3]
        self.time_cpu_cycles = values[4]
        self.num_detected_obj = values[5]
        self.num_tlvs = values[6]  # Ensure this line is correct
        self.sub_frame_index = values[7]

    def __str__(self):
        return (f"FrameHeader(version={self.version}, total_packet_len={self.total_packet_len}, "
                f"platform={self.platform}, frame_number={self.frame_number}, "
                f"time_cpu_cycles={self.time_cpu_cycles}, num_detected_obj={self.num_detected_obj}, "
                f"num_tlvs={self.num_tlvs}, sub_frame_index={self.sub_frame_index})")

class DetectedObjectsTLV:
    def __init__(self, num_objects, data):
        self.num_detected_obj = num_objects
        self.objects = []
        for i in range(num_objects):
            start = i * struct.calcsize(DETECTED_OBJ_STRUCT_FORMAT)
            end = start + struct.calcsize(DETECTED_OBJ_STRUCT_FORMAT)
            object_data = struct.unpack(DETECTED_OBJ_STRUCT_FORMAT, data[start:end])
            self.objects.append({
                'x': object_data[1],
                'y': object_data[2],
                'z': object_data[3]
            })

def read_and_process_tlvs(ser, num_tlvs):
    objects = []
    for _ in range(num_tlvs):
        tlv_header_data = ser.read(struct.calcsize(TLV_HEADER_FORMAT))
        tlv_type, tlv_length = struct.unpack(TLV_HEADER_FORMAT, tlv_header_data)
        tlv_data = ser.read(tlv_length - struct.calcsize(TLV_HEADER_FORMAT))

        if tlv_type == 1:  # Detected Objects TLV
            num_objects = struct.unpack('<H', tlv_data[:2])[0]
            # Further processing of TLV data

    return objects


def find_sync(ser):
    sync_bytes = b''
    while True:
        byte = ser.read(1)
        sync_bytes += byte
        if sync_bytes.endswith(SYNC_PATTERN):
            return True
    return False

def read_frame_header(ser):
    if find_sync(ser):
        header_data = ser.read(struct.calcsize(FRAME_HEADER_FORMAT))
        return FrameHeader(header_data)
    return None


def update_plot(frame, ser, scatter_plot, ax):
    frame_header = read_frame_header(ser)
    if frame_header:
        objects = read_and_process_tlvs(ser, frame_header.num_tlvs)
        if objects:
            xs = [obj['x'] for obj in objects]
            ys = [obj['y'] for obj in objects]
            scatter_plot.set_offsets(np.c_[xs, ys])
            ax.relim()
            ax.autoscale_view()

def main():
    with serial.Serial('/dev/ttyACM1', 921600) as ser:
        fig, ax = plt.subplots()
        scatter_plot = ax.scatter([], [], s=100)
        ani = FuncAnimation(fig, update_plot, fargs=(ser, scatter_plot, ax), interval=50)
        plt.show()

if __name__ == "__main__":
    main()

