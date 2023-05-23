import re
from typing import Optional

from returns.maybe import Maybe, Nothing, Some
from returns.result import safe

from dino_seedwork_be.domain.value_object.AbstractValueObject import \
    ValueObject

# __all__ = ["StringWithRegex"]


class StringWithRegex(ValueObject):
    _pattern: str
    _value: Maybe[str] = Nothing
    _error_message: str = "Value does not path the pattern: "

    def __init__(self, a_regex: str, an_error_message: Optional[str] = None):
        self.set_pattern(a_regex)
        if an_error_message is not None:
            self._error_message = an_error_message

    @safe
    def set_value(
        self,
        a_value: Maybe[str],
        exception_code: Maybe[str] = Nothing,
        loc: Maybe[list[str]] = Nothing,
    ):
        match a_value:
            case str():
                self.assert_state_true(
                    re.match(self._pattern, a_value) is not None,
                    Some(f"{self._error_message} {a_value}"),
                    code=exception_code,
                    loc=loc,
                ).unwrap()
                self._value = a_value
            case None:
                self._value = Nothing

    def set_pattern(self, a_regex: str):
        self.assert_argument_not_empty(
            Some(a_regex), Some("Pattern for a StringRegex cannot be empty")
        ).unwrap()
        self._pattern = a_regex

    def value(self) -> Maybe[str]:
        return self._value
