from returns.maybe import Some

from dino_seedwork_be.domain.exceptions import DomainException
from dino_seedwork_be.domain.value_object.AbstractValueObject import \
    ValueObject

# __all__ = ["FullName"]


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
            self.assert_argument_not_empty(
                Some(a_value), Some("First name is required")
            ).unwrap()
            self.assert_argument_length(
                a_value,
                a_minimum=1,
                a_maximum=50,
                a_message=Some("First name must be 50 characters or less"),
            ).unwrap()
            self.assert_argument_regex(
                a_value,
                r"^[A-Z\s](?:[A-Za-z_ÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚĂĐĨŨƠàáâãèéêìíòóôõùúăđĩũơƯĂẠẢẤẦẨẪẬẮẰẲẴẶẸẺẼỀỀỂưăạảấầẩẫậắằẳẵặẹẻẽềềểỄỆỈỊỌỎỐỒỔỖỘỚỜỞỠỢỤỦỨỪễếệỉịọỏốồổỗộớờởỡợụủứừỬỮỰỲỴÝỶỸửữựỳỵỷỹ\s])+$",
                Some(
                    "First name must be at least one character in length, \
                starting with a capital letter."
                ),
            ).unwrap()
            self._first_name = a_value
        except Exception as error:
            raise DomainException(code="FIRST_NAME_INVALID", message=str(error))

    def _set_last_name(self, a_value: str):
        try:
            self.assert_argument_not_empty(
                Some(a_value), Some("Last name is required")
            ).unwrap()
            self.assert_argument_length(
                a_value,
                a_minimum=1,
                a_maximum=50,
                a_message=Some("last name must be 50 characters or less"),
            ).unwrap()
            self.assert_argument_regex(
                a_value,
                r"^[A-Z\s](?:[A-Za-z_ÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚĂĐĨŨƠàáâãèéêìíòóôõùúăđĩũơƯĂẠẢẤẦẨẪẬẮẰẲẴẶẸẺẼỀỀỂưăạảấầẩẫậắằẳẵặẹẻẽềềểỄỆỈỊỌỎỐỒỔỖỘỚỜỞỠỢỤỦỨỪễếệỉịọỏốồổỗộớờởỡợụủứừỬỮỰỲỴÝỶỸửữựỳỵỷỹ\s])+$",
                Some("Last name must be at least one character in length."),
            ).unwrap()
            self._last_name = a_value
        except Exception as error:
            raise DomainException(code="LAST_NAME_INVALID", message=str(error))
