import struct
from src.saveable.saveable import SaveableType
from src.saveable.saveableInt import saveable_int


class SaveableString(SaveableType):
    def __init__(self, value=''):
        self.value = value

    def set(self, value):
        self.value = value

    def get(self):
        return self.value

    def load_in_place(self, byte_array):
        self.value = ''
        length = saveable_int('u32').from_byte_array(byte_array)
        for _ in range(length.value):
            char = struct.unpack('c', bytes((byte_array[0],)))
            self.value += char[0].decode('ascii')
            byte_array.pop(0)

    def to_byte_array(self):
        length = saveable_int('u32')()
        length.set(len(self.value))
        array = length.to_byte_array()
        for char in list(self.value):
            p_char = int.from_bytes(struct.pack('c', char.encode('ascii')), byteorder='big')
            array.append(p_char)
        return array

    def __str__(self):
        return self.value