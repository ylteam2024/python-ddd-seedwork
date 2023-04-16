import uuid
from typing import BinaryIO, List, Optional

import validators

from dino_seedwork_be.utils import (get_image_dimension, get_image_file_size,
                                    is_url_image)

from .DomainAssertionConcern import DomainAssertionConcern
from .exceptions import DomainException

UUID = uuid.UUID
UUID_v4 = uuid.uuid4

__all__ = [
    "ValueObject",
    "ImageURL",
    "URL",
    "FullName",
    "File",
    "FirstNameValidationFailed",
    "LastNameValidationFailed",
]


class ValueObject(DomainAssertionConcern):

    """
    Base class for value objects
    """


class ImageURL(ValueObject):
    _url: str

    def __init__(self, url: str, validate_url: Optional[bool] = False):
        self.set_url(url, validate_url)
        super().__init__()

    def set_url(self, url: str, validate_url: Optional[bool] = False):
        self.assert_argument_not_empty(
            url, a_message="url string cannot be None"
        ).unwrap()
        validators.url(url)
        if validate_url:
            self.assert_state_true(
                is_url_image(url), "url is not a valid url image"
            ).unwrap()
        self._url = url

    def url(self) -> str:
        return self._url


class URL(ValueObject):
    _value: str
    _regex: str = r"https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,4}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)"

    def __eq__(self, other):
        if isinstance(other, URL):
            return self.getValue() == other.getValue()
        return False

    def __init__(
        self,
        value: str,
        validation_message: Optional[str] = None,
        loc: Optional[List[str]] = ["url"],
    ):
        self.assert_argument_regex(
            value, self._regex, a_message=validation_message, loc=loc
        ).unwrap()
        self._value = value
        super().__init__()

    def getValue(self):
        return self._value


class File:
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


class FirstNameValidationFailed(DomainException):
    pass


class LastNameValidationFailed(DomainException):
    pass


class FullName(ValueObject):
    _first_name: str | None = None
    _last_name: str | None = None

    def __init__(self, first_name: str | None, last_name: str | None):
        super().__init__()
        if first_name is not None:
            self._set_first_name(first_name)
        if last_name is not None:
            self._set_last_name(last_name)

    def __eq__(self, obj):
        if isinstance(obj, FullName):
            return (
                self.first_name() == obj.first_name()
                and self.last_name() == obj.last_name()
            )
        return False

    def first_name(self) -> str | None:
        return self._first_name

    def last_name(self) -> str | None:
        return self._last_name

    def as_formatted_name(self):
        return f"{self._last_name} {self._first_name}"

    def with_changed_first_name(self, aFirstName: str):
        return FullName(first_name=aFirstName, last_name=self._last_name)

    def with_changed_last_name(self, aSecondName: str):
        return FullName(last_name=aSecondName, first_name=self._first_name)

    def _set_first_name(self, a_value: str):
        try:
            self.assert_argument_not_empty(a_value, "First name is required").unwrap()
            self.assert_argument_length(
                a_value,
                a_minimum=1,
                a_maximum=50,
                a_message="First name must be 50 characters or less",
            ).unwrap()
            self.assert_argument_regex(
                a_value,
                r"^[A-Z\s](?:[A-Za-z_ÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚĂĐĨŨƠàáâãèéêìíòóôõùúăđĩũơƯĂẠẢẤẦẨẪẬẮẰẲẴẶẸẺẼỀỀỂưăạảấầẩẫậắằẳẵặẹẻẽềềểỄỆỈỊỌỎỐỒỔỖỘỚỜỞỠỢỤỦỨỪễếệỉịọỏốồổỗộớờởỡợụủứừỬỮỰỲỴÝỶỸửữựỳỵỷỹ\s])+$",
                "First name must be at least one character in length, \
                starting with a capital letter.",
            ).unwrap()
            self._first_name = a_value
        except Exception as error:
            raise FirstNameValidationFailed(str(error))

    def _set_last_name(self, a_value: str):
        try:
            self.assert_argument_not_empty(a_value, "Last name is required").unwrap()
            self.assert_argument_length(
                a_value,
                a_minimum=1,
                a_maximum=50,
                a_message="last name must be 50 characters or less",
            ).unwrap()
            self.assert_argument_regex(
                a_value,
                r"^[A-Z\s](?:[A-Za-z_ÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚĂĐĨŨƠàáâãèéêìíòóôõùúăđĩũơƯĂẠẢẤẦẨẪẬẮẰẲẴẶẸẺẼỀỀỂưăạảấầẩẫậắằẳẵặẹẻẽềềểỄỆỈỊỌỎỐỒỔỖỘỚỜỞỠỢỤỦỨỪễếệỉịọỏốồổỗộớờởỡợụủứừỬỮỰỲỴÝỶỸửữựỳỵỷỹ\s])+$",
                "Last name must be at least one character in length.",
            ).unwrap()
            self._last_name = a_value
        except Exception as error:
            raise LastNameValidationFailed(str(error))
