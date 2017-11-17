import io
from PIL import Image

from src.saveable.saveable import SaveableType
from src.saveable.saveableInt import saveable_int


class SaveableImage(SaveableType):
    """
    A Saveable image type that can hold PIL images
    """
    def __init__(self, image=None):
        self.image = image

    def set(self, value):
        if not isinstance(value, Image.Image):
            raise ValueError('{} is not an image type'.format(value))
        self.image = value

    def get(self):
        return self.image

    def load_in_place(self, byte_array):
        size = saveable_int('u32').from_byte_array(byte_array)
        stream = io.BytesIO(byte_array)
        self.image = Image.open(stream)
        self.image.load()
        stream.close()
        del byte_array[:size.value]

    def to_byte_array(self):
        _bytes = io.BytesIO()
        self.image.save(_bytes, format=self.image.format)
        size = saveable_int('u32')()
        size.set(len(_bytes.getvalue()))
        return size.to_byte_array() + bytearray(_bytes.getvalue())

