from typing import BinaryIO

from dino_seedwork_be.domain.value_object.AbstractValueObject import \
    ValueObject
from dino_seedwork_be.utils.image import (get_image_dimension,
                                          get_image_file_size)

# __all__ = ["File"]


class File(ValueObject):
    _file: BinaryIO
    _content_type: str
    _name: str

    def __init__(self, file: BinaryIO, contentType: str, name: str):
        self._file = file
        self._content_type = contentType
        self._name = name
        super().__init__()

    def dimension(self):
        return get_image_dimension(self.file())

    def size(self) -> float:
        return get_image_file_size(self.file())

    def name(self) -> str:
        return self._name

    def contentType(self):
        return self._content_type

    def file(self):
        return self._file
