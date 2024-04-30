import struct

class DetectedObjectsTLV:
    def __init__(self, data):
        self.num_detected_obj, self.xyzQFormat = struct.unpack('<HH', data[:4])
        self.objects = []

        offset = 4
        object_size = 12  # Each object has 12 bytes of data

        for _ in range(self.num_detected_obj):
            object_data = struct.unpack('<6h', data[offset:offset + object_size])
            detected_object = {
                'speedIdx': object_data[0],
                'x': object_data[1] / (2 ** self.xyzQFormat),
                'y': object_data[2] / (2 ** self.xyzQFormat),
                'z': object_data[3] / (2 ** self.xyzQFormat),
                'rangeIdx': object_data[4],
                'peakVal': object_data[5]
            }
            self.objects.append(detected_object)
            offset += object_size

    def __str__(self):
        return f"DetectedObjectsTLV(num_detected_obj={self.num_detected_obj}, objects={self.objects})"

