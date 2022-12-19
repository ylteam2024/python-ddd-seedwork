import uuid
from typing import BinaryIO, List, Optional, Union

import validators

from dino_seedwork_be.domain.assertion_concern import DomainAssertionConcern
from dino_seedwork_be.domain.exceptions import DomainException
from dino_seedwork_be.exceptions import IllegalArgumentException
from dino_seedwork_be.utils.image import (get_image_dimension,
                                          get_image_file_size)
from dino_seedwork_be.utils.validator import is_url_image

UUID = uuid.UUID
UUID_v4 = uuid.uuid4


class ValueObject(DomainAssertionConcern):
    """
    Base class for value objects
    """


class ID(ValueObject):
    __id: UUID

    def __init__(self, id: Union[UUID, str]):

        if isinstance(id, UUID):
            self.setID(id)
        elif isinstance(id, str):
            self.setID(UUID(id))
        else:
            raise IllegalArgumentException("id should be UUID or UUID string")
        super().__init__()

    def __eq__(self, obj):
        return self.__id == obj.__id

    def equals(self, obj: object) -> bool:
        isEqual = False
        if isinstance(obj, ID):
            isEqual = self.__id == obj.__id
        return isEqual

    def setID(self, id: UUID | str):
        self.assertArgumentNotEmpty(str(id), "The id must be provided")
        self.assertArgumentLength(
            str(id),
            aMinimum=0,
            aMaximum=36,
            aMessage="The id must be 36 characters or less.",
        )
        match id:
            case str() as id:
                self.__id = UUID(id)
            case UUID() as id:
                self.__id = id

    def getRaw(self) -> str:
        return str(self.__id)

    @staticmethod
    def getRawString(id: "ID"):
        return id.getRaw()


def idFromString(id: str | ID) -> ID:
    match id:
        case str():
            return ID(id)
        case ID():
            return id


class ImageURL(ValueObject):
    url: str

    def __init__(self, url: str, validateUrl: Optional[bool] = False):
        self.setUrl(url, validateUrl)
        super().__init__()

    def setUrl(self, url: str, validateUrl: Optional[bool] = False):
        self.assertArgumentNotEmpty(url, aMessage="url string cannot be None")
        validators.url(url)
        if validateUrl:
            self.assertStateTrue(is_url_image(url), "url is not a valid url image")
        self.url = url

    def getUrl(self) -> str:
        return self.url


class URL(ValueObject):
    value: str
    regex: str = r"https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,4}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)"

    def __eq__(self, other):
        if isinstance(other, URL):
            return self.getValue() == other.getValue()
        return False

    def __init__(
        self,
        value: str,
        validationMessage: Optional[str] = None,
        loc: Optional[List[str]] = ["url"],
    ):
        self.assertArgumentRegex(value, self.regex, aMessage=validationMessage, loc=loc)
        self.value = value
        super().__init__()

    def getValue(self):
        return self.value


class File:
    __file: BinaryIO
    __contentType: str
    __name: str

    def __init__(self, file: BinaryIO, contentType: str, name: str):
        self.__file = file
        self.__contentType = contentType
        self.__name = name
        super().__init__()

    def dimension(self):
        return get_image_dimension(self.file())

    def size(self) -> float:
        return get_image_file_size(self.file())

    def name(self) -> str:
        return self.__name

    def contentType(self):
        return self.__contentType

    def file(self):
        return self.__file


class FirstNameValidationFailed(DomainException):
    pass


class LastNameValidationFailed(DomainException):
    pass


class FullName(ValueObject):
    __firstName: str | None = None
    __lastName: str | None = None

    def __init__(self, firstName: str | None, lastName: str | None):
        super().__init__()
        if firstName is not None:
            self.__setFirstName(firstName)
        if lastName is not None:
            self.__setLastName(lastName)

    def __eq__(self, obj):
        if isinstance(obj, FullName):
            return (
                self.getFirstName() == obj.getFirstName()
                and self.getLastName() == obj.getLastName()
            )
        return False

    def getFirstName(self) -> str | None:
        return self.__firstName

    def getLastName(self) -> str | None:
        return self.__lastName

    def asFormattedName(self):
        return f"{self.__lastName} {self.__firstName}"

    def withChangedFirstName(self, aFirstName: str):
        return FullName(firstName=aFirstName, lastName=self.__lastName)

    def withChangedLastName(self, aSecondName: str):
        return FullName(lastName=aSecondName, firstName=self.__firstName)

    def __setFirstName(self, aValue: str):
        try:
            self.assertArgumentNotEmpty(aValue, "First name is required")
            self.assertArgumentLength(
                aValue,
                aMinimum=1,
                aMaximum=50,
                aMessage="First name must be 50 characters or less",
            )
            self.assertArgumentRegex(
                aValue,
                r"^[A-Z\s](?:[A-Za-z_ÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚĂĐĨŨƠàáâãèéêìíòóôõùúăđĩũơƯĂẠẢẤẦẨẪẬẮẰẲẴẶẸẺẼỀỀỂưăạảấầẩẫậắằẳẵặẹẻẽềềểỄỆỈỊỌỎỐỒỔỖỘỚỜỞỠỢỤỦỨỪễếệỉịọỏốồổỗộớờởỡợụủứừỬỮỰỲỴÝỶỸửữựỳỵỷỹ\s])+$",
                "First name must be at least one character in length, \
                starting with a capital letter.",
            )
            self.__firstName = aValue
        except Exception as error:
            raise FirstNameValidationFailed(str(error))

    def __setLastName(self, aValue: str):
        try:
            self.assertArgumentNotEmpty(aValue, "Last name is required")
            self.assertArgumentLength(
                aValue,
                aMinimum=1,
                aMaximum=50,
                aMessage="last name must be 50 characters or less",
            )
            self.assertArgumentRegex(
                aValue,
                r"^[A-Z\s](?:[A-Za-z_ÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚĂĐĨŨƠàáâãèéêìíòóôõùúăđĩũơƯĂẠẢẤẦẨẪẬẮẰẲẴẶẸẺẼỀỀỂưăạảấầẩẫậắằẳẵặẹẻẽềềểỄỆỈỊỌỎỐỒỔỖỘỚỜỞỠỢỤỦỨỪễếệỉịọỏốồổỗộớờởỡợụủứừỬỮỰỲỴÝỶỸửữựỳỵỷỹ\s])+$",
                "Last name must be at least one character in length.",
            )
            self.__lastName = aValue
        except Exception as error:
            raise LastNameValidationFailed(str(error))
