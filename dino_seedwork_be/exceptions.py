import enum
from typing import List, Optional

from returns.maybe import Maybe


class NotImplementError(RuntimeError):
    def __init__(self, message: str):
        super().__init__(f"NotImplementError: {message}")


class ExceptionCode(enum.Enum):
    RAW_EXCEPTION = "RAW_EXCEPTION"


class MainException(Exception):
    _code: Optional[str] = ExceptionCode.RAW_EXCEPTION.value
    _message: Optional[str] = None
    _loc: Optional[List[str]] = None

    def __init__(
        self,
        code: Optional[str] = None,
        message: Optional[str] = None,
        loc: Optional[List[str]] = None,
    ):
        super().__init__(f"[{code}]: {message} at {loc}")
        self._code = code
        self._message = message
        self._loc = loc

    def message(self) -> Maybe[str]:
        return Maybe.from_optional(self._message)

    def set_loc(self, loc: List[str]):
        self._loc = loc

    def loc(self) -> Maybe[List[str]]:
        return Maybe.from_optional(self._loc)

    def code(self) -> Maybe[str]:
        return Maybe.from_optional(self._code)

    def where(self) -> Maybe[List[str]]:
        return Maybe.from_optional(self._loc)


class IllegalArgumentException(MainException):
    def __init__(
        self,
        message: Optional[str],
        loc: Optional[List[str]] = None,
        code: Optional[str] = None,
    ):
        super().__init__(
            message=f"IllegalArgumentException: {message} - loc: {loc}",
            loc=loc,
            code=code,
        )


class IllegalStateException(MainException):
    def __init__(
        self,
        message: Optional[str],
        loc: Optional[List[str]] = None,
        code: Optional[str] = None,
    ):
        super().__init__(
            message=f"IllegalStateException: {message} - loc: {loc}", loc=loc, code=code
        )


def except_locs(locs: List[str]):
    def decor(function):
        def wrapper(*args, **kwargs):
            try:
                return function(*args, **kwargs)
            except MainException as error:
                current_locs = error.loc().value_or([])
                if len(locs) <= len(current_locs):
                    is_begin_sub_array = all(
                        [elem == current_locs[idx] for idx, elem in enumerate(locs)]
                    )
                    if is_begin_sub_array:
                        raise error
                error.set_loc([*locs, *current_locs])
                raise error

        return wrapper

    return decor
