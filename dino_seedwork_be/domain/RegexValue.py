import re
from typing import Optional

from dino_seedwork_be.domain.assertion_concern import DomainAssertionConcern
from dino_seedwork_be.domain.value_objects import ValueObject


class StringWithRegex(ValueObject, DomainAssertionConcern):
    pattern: str
    value: str | None = None
    errorMessage: str = "Value does not path the pattern: "

    def __init__(self, aRegex: str, anErrorMessage: Optional[str] = None):
        self.setPattern(aRegex)
        if anErrorMessage is not None:
            self.errorMessage = anErrorMessage

    def setValue(
        self,
        aValue: Optional[str],
        exceptionCode: Optional[str] = None,
        loc: Optional[list[str]] = None,
    ):
        match aValue:
            case str():
                self.assertStateTrue(
                    re.match(self.pattern, aValue) is not None,
                    f"{self.errorMessage} {aValue}",
                    code=exceptionCode,
                    loc=loc,
                )
                self.value = aValue
            case None:
                self.value = None

    def setPattern(self, aRegex: str):
        self.assertArgumentNotEmpty(aRegex, "Pattern for a StringRegex cannot be empty")
        self.pattern = aRegex

    def getValue(self) -> str | None:
        return self.value
