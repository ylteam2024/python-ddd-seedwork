from typing import List

from returns.maybe import Maybe, Nothing, Some

from dino_seedwork_be.domain.value_object.AbstractValueObject import \
    ValueObject

# __all__ = ["URL"]


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
        validation_message: Maybe[str] = Nothing,
        loc: List[str] = ["url"],
    ):
        self.assert_argument_regex(
            value, self._regex, a_message=validation_message, loc=Some(loc)
        ).unwrap()
        self._value = value
        super().__init__()

    def getValue(self):
        return self._value
