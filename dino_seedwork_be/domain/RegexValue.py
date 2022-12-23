import re
from typing import Optional

from dino_seedwork_be.domain import ValueObject
from dino_seedwork_be.logic import DomainAssertionConcern

__all__ = ["StringWithRegex"]


class StringWithRegex(ValueObject, DomainAssertionConcern):
    _pattern: str
    _value: str | None = None
    _error_message: str = "Value does not path the pattern: "

    def __init__(self, a_regex: str, an_error_message: Optional[str] = None):
        self.set_pattern(a_regex)
        if an_error_message is not None:
            self._error_message = an_error_message

    def set_value(
        self,
        a_value: Optional[str],
        exception_code: Optional[str] = None,
        loc: Optional[list[str]] = None,
    ):
        match a_value:
            case str():
                self.assert_state_true(
                    re.match(self._pattern, a_value) is not None,
                    f"{self._error_message} {a_value}",
                    code=exception_code,
                    loc=loc,
                ).unwrap()
                self._value = a_value
            case None:
                self._value = None

    def set_pattern(self, aRegex: str):
        self.assert_argument_not_empty(
            aRegex, "Pattern for a StringRegex cannot be empty"
        ).unwrap()
        self._pattern = aRegex

    def value(self) -> str | None:
        return self._value
