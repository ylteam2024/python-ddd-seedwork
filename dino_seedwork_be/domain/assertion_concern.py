import re
from typing import Optional, Union, overload

from dino_seedwork_be.domain.exceptions import (DomainIllegalArgumentException,
                                                DomainIllegalStateException)


class AssertionConcern:
    __IllegalArgExceptionCls = DomainIllegalArgumentException
    __IllegalStExceptionCls = DomainIllegalStateException

    def assertArgumentEquals(
        self,
        anObject1: object,
        anObject2: object,
        aMessage: str,
        loc: Optional[list[str]] = None,
        code: Optional[str] = None,
    ):
        if anObject1 != anObject2:
            raise self.__IllegalArgExceptionCls(aMessage, loc=loc, code=code)

    def assertArgumentFalse(
        self,
        aBoolean: bool,
        aMessage: str,
        loc: Optional[list[str]] = None,
        code: Optional[str] = None,
    ):
        if aBoolean:
            raise self.__IllegalArgExceptionCls(
                f"Must be False: {aMessage}", loc=loc, code=code
            )

    def assertArgumentTrue(
        self,
        aBoolean: bool,
        aMessage: str,
        loc: Optional[list[str]] = None,
        code: Optional[str] = None,
    ):
        if not aBoolean:
            raise self.__IllegalArgExceptionCls(
                f"Must be False: {aMessage}", loc=loc, code=code
            )

    def assertArgumentLength(
        self,
        aString: str,
        aMaximum: int,
        aMinimum: int,
        aMessage: str,
        loc: Optional[list[str]] = None,
        code: Optional[str] = None,
    ):
        length = len(aString.strip())
        if length > aMaximum:
            raise self.__IllegalArgExceptionCls(
                f"Length must be less than {aMaximum}: {aMessage}", loc=loc, code=code
            )

        if length < aMinimum:
            raise self.__IllegalArgExceptionCls(
                f"Length must be large than {aMinimum}: {aMessage}", loc=loc
            )

    def assertArgumentNotEmpty(
        self,
        aString: str,
        aMessage: str,
        loc: Optional[list[str]] = None,
        code: Optional[str] = None,
    ):
        if aString is None or len(aString.strip()) == 0:
            raise self.__IllegalArgExceptionCls(
                f"String not empty: {aMessage}", loc=loc, code=code
            )

    def assertArgumentNotEquals(
        self,
        anObject1: object,
        anObject2: object,
        aMessage: str,
        loc: Optional[list[str]] = None,
        code: Optional[str] = None,
    ):
        if anObject1 == anObject2:
            raise self.__IllegalArgExceptionCls(
                f"Argument must be equal: {aMessage}", loc=loc, code=code
            )

    def assertArgumentNotNull(
        self,
        anObject: object,
        aMessage: str,
        loc: Optional[list[str]] = None,
        code: Optional[str] = None,
    ):
        if anObject is None:
            raise self.__IllegalArgExceptionCls(
                f"Argument cannot be null: {aMessage}", loc=loc, code=code
            )

    def assertArgumentLargerThan(
        self,
        aValue: Union[int, float],
        aMinium: Union[int, float],
        aMessage: str = "",
        allowEqual: bool = False,
        loc: Optional[list[str]] = None,
        code: Optional[str] = None,
    ):
        if (aValue <= aMinium) and (not allowEqual and aValue < aMinium):
            raise self.__IllegalArgExceptionCls(
                f"Argument must be in larger than {aMinium}: {aMessage} but {aValue} is not",
                loc=loc,
                code=code,
            )

    def assertArgumentSmallerThan(
        self,
        aValue: Union[int, float],
        aMaximum: Union[int, float],
        aMessage: str = "",
        allowEqual: bool = False,
        loc: Optional[list[str]] = None,
        code: Optional[str] = None,
    ):
        if aValue >= aMaximum and (not allowEqual and aValue > aMaximum):
            raise self.__IllegalArgExceptionCls(
                f"Argument must be in smaller than {aMaximum}: {aMessage}",
                loc=loc,
                code=code,
            )

    @overload
    def assertArgumentRange(
        self,
        aValue: int,
        aMinium: int,
        aMaximum: float,
        aMessage: str,
        loc: Optional[list[str]] = None,
        code: Optional[str] = None,
    ):
        ...

    @overload
    def assertArgumentRange(
        self,
        aValue: float,
        aMinium: float,
        aMaximum: float,
        aMessage: str,
        loc: Optional[list[str]] = None,
        code: Optional[str] = None,
    ):
        ...

    def assertArgumentRange(
        self,
        aValue,
        aMinium,
        aMaximum,
        aMessage,
        loc=None,
        code: Optional[str] = None,
    ):
        if aValue < aMinium or aValue > aMaximum:
            raise self.__IllegalArgExceptionCls(
                f"Length must in range {aMinium} -> {aMaximum}: {aMessage}",
                loc=loc,
                code=code,
            )

    def assertArgumentRegex(
        self,
        aValue: str,
        regex: str,
        aMessage: Optional[str] = "",
        loc: Optional[list[str]] = None,
        code: Optional[str] = None,
    ):
        print("regex check ", aValue, re.match(regex, aValue))
        if re.match(regex, aValue) is None:
            raise self.__IllegalArgExceptionCls(
                f"Argument does not match the required regex pattern: {aMessage} with value {aValue}",
                loc=loc,
                code=code,
            )

    def assertStateTrue(
        self,
        aBoolean: bool,
        aMessage: str,
        loc: Optional[list[str]] = None,
        code: Optional[str] = None,
    ):
        if not aBoolean:
            raise self.__IllegalStExceptionCls(aMessage, code=code, loc=loc)

    def assertStateFalse(
        self,
        aBoolean: bool,
        aMessage: str,
        loc: Optional[list[str]] = None,
        code: Optional[str] = None,
    ):
        if aBoolean:
            raise self.__IllegalStExceptionCls(aMessage, loc=loc, code=code)


class DomainAssertionConcern(AssertionConcern):
    __IllegalArgExceptionCls = DomainIllegalArgumentException
    __IllegalStExceptionCls = DomainIllegalStateException
