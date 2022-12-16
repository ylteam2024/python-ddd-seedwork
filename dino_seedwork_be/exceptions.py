import enum
from typing import List, Optional

from returns.maybe import Maybe


class NotImplementError(RuntimeError):
    def __init__(self, message: str):
        super().__init__(f"NotImplementError: {message}")


class ExceptionCode(enum.Enum):
    RAW_EXCEPTION = "RAW_EXCEPTION"


class MainException(Exception):
    __code: Optional[str] = ExceptionCode.RAW_EXCEPTION.value
    __message: Optional[str] = None
    __loc: Optional[List[str]] = None

    def __init__(
        self,
        code: Optional[str] = None,
        message: Optional[str] = None,
        loc: Optional[List[str]] = None,
    ):
        super().__init__(f"[{code}]: {message} at {loc}")
        self.__code = code
        self.__message = message
        self.__loc = loc

    def getMessage(self) -> Maybe[str]:
        return Maybe.from_optional(self.__message)

    def setLoc(self, loc: List[str]):
        self.__loc = loc

    def getLoc(self) -> Maybe[List[str]]:
        return Maybe.from_optional(self.__loc)

    def getCode(self) -> Maybe[str]:
        return Maybe.from_optional(self.__code)

    def where(self) -> Maybe[List[str]]:
        return Maybe.from_optional(self.__loc)


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
                currentLocs = error.getLoc().value_or([])
                if len(locs) <= len(currentLocs):
                    isBeginSubArray = all([elem == currentLocs[idx] for idx, elem in enumerate(locs)])
                    if isBeginSubArray:
                        raise error 
                error.setLoc([*locs, *currentLocs])
                raise error
        return wrapper
    return decor


