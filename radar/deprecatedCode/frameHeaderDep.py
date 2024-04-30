import serial
import struct
class FrameHeader:

    STRUCT_FORMAT = '<IIIIIIII'  # Little endian, 8 bytes for sync, followed by 8 unsigned integers
    def __init__(self, sync, data):
        unpacked_data = struct.unpack(self.STRUCT_FORMAT, data)
        self.sync = sync
        self.version = unpacked_data[0]
        self.total_packet_len = unpacked_data[1]
        self.platform = unpacked_data[2]
        self.frame_number = unpacked_data[3]
        self.time_cpu_cycles = unpacked_data[4]
        self.num_detected_obj = unpacked_data[5]
        self.num_tlvs = unpacked_data[6]
        self.sub_frame_index = unpacked_data[7]
    def __str__(self):
        return (
        f"FrameHeader(sync={self.sync!r}, "
        f"version={self.version}, "
        f"total_packet_len={self.total_packet_len}, "
        f"platform={self.platform}, "
        f"frame_number={self.frame_number}, "
        f"time_cpu_cycles={self.time_cpu_cycles}, "
        f"num_detected_obj={self.num_detected_obj}, "
        f"num_tlvs={self.num_tlvs}, "
        f"sub_frame_index={self.sub_frame_index})"
                )
