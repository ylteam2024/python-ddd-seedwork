import re
from enum import Enum
from typing import List, Optional, Union, overload

from returns.future import FutureFailure, FutureResult, FutureSuccess
from returns.maybe import Maybe, Some
from returns.result import Result, Success

from dino_seedwork_be.domain.exceptions import (DomainIllegalArgumentException,
                                                DomainIllegalStateException)
from dino_seedwork_be.exceptions import (IllegalArgumentException,
                                         IllegalStateException)
from dino_seedwork_be.utils.functional import return_v


class AssertionErrorCode(Enum):
    ARG_CANNOT_EQUAL = "CANNOT_EQUAL"
    ARG_CANNOT_BE_FALSE = "CANNOT_BE_FALSE"
    ARG_CANNOT_BE_TRUE = "CANNOT_BE_TRUE"
    ARG_LENGTH_INVALID = "LENGTH_INVALID"
    ARG_STRING_CANNOT_EMPTY = "STRING_CANNOT_EMPTY"
    ARG_CANNOT_BE_NONE = "CANNOT_BE_NONE"
    ARG_SHOULD_EQUALS = "NOT_EQUALS"
    ARG_NOT_EQUALS = "NOT_EQUALS"
    ARG_NOT_LARGER_THAN = "NOT_LARGER_THAN"
    ARG_NOT_SMALLER_THAN = "NOT_SMALLER_THAN"
    ARG_NOT_IN_RANGE = "NOT_IN_RANGE"
    ARG_NOT_REGEX_MATCHED = "NOT_REGEX_MATCHED"
    STATE_NOT_SATISFIED = "STATE_NOT_STATISFIED"
    STATE_CANNOT_STATISFIED = "STATE_CANNOT_STATISFIED"


class AssertionConcern:
    __IllegalArgExceptionCls = IllegalArgumentException
    __IllegalStExceptionCls = IllegalStateException

    @staticmethod
    def simple_handle_on_bool_val(aBool: bool, exception: Optional[Exception]):
        """
        Throw if a_bool is True
        """
        match aBool:
            case True:
                return Result.from_failure(exception)
        return Result.from_value("OK")

    def assert_argument_equals(
        self,
        an_obj1: object,
        an_obj2: object,
        a_message: Optional[str] = None,
        exception: Optional[Exception] = None,
        loc: Optional[List[str]] = None,
        code: Optional[str] = None,
    ) -> Result:
        isNotEqual = an_obj1 != an_obj2
        return AssertionConcern.simple_handle_on_bool_val(
            isNotEqual,
            exception
            or self.__IllegalArgExceptionCls(
                message=a_message,
                code=code or AssertionErrorCode.ARG_SHOULD_EQUALS.value,
                loc=loc,
            ),
        )

    def assert_argument_false(
        self,
        a_boolean: bool,
        a_message: Optional[str] = None,
        exception: Optional[Exception] = None,
        loc: Optional[List[str]] = None,
        code: Optional[str] = None,
    ) -> Result:
        isFalse = not a_boolean
        return AssertionConcern.simple_handle_on_bool_val(
            not isFalse,
            exception
            or self.__IllegalArgExceptionCls(
                f"Must be False: {a_message}",
                code=code or AssertionErrorCode.ARG_CANNOT_BE_TRUE.value,
                loc=loc,
            ),
        )

    def assert_argument_true(
        self,
        a_boolean: bool,
        a_message: Optional[str] = None,
        exception: Optional[Exception] = None,
        loc: Optional[List[str]] = None,
        code: Optional[str] = None,
    ) -> Result:
        isTrue = a_boolean
        return AssertionConcern.simple_handle_on_bool_val(
            not isTrue,
            exception
            or self.__IllegalArgExceptionCls(
                f"Must be True: {a_message}",
                code=code or AssertionErrorCode.ARG_CANNOT_BE_FALSE.value,
                loc=loc,
            ),
        )

    def assert_argument_length(
        self,
        aString: str,
        a_minimum: int,
        a_maximum: int,
        a_message: Optional[str] = None,
        exception: Optional[Exception] = None,
        loc: Optional[List[str]] = None,
        code: Optional[str] = None,
    ) -> Result:
        length = len(aString.strip())
        match length > a_maximum:
            case True:
                return Result.from_failure(
                    exception
                    or self.__IllegalArgExceptionCls(
                        f"Length must be less than {a_maximum} but {aString} is not: {a_message}",
                        code=code or AssertionErrorCode.ARG_LENGTH_INVALID.value,
                        loc=loc,
                    ),
                )

        match length < a_minimum:
            case True:
                return Result.from_failure(
                    exception
                    or self.__IllegalArgExceptionCls(
                        f"Length must be large than {a_minimum}: {a_message}",
                        code=code or AssertionErrorCode.ARG_LENGTH_INVALID.value,
                        loc=loc,
                    )
                )
        return Success(aString)

    def assert_argument_not_empty(
        self,
        a_string: str,
        a_message: Optional[str] = None,
        exception: Optional[Exception] = None,
        loc: Optional[List[str]] = None,
        code: Optional[str] = None,
    ) -> Result:
        isEmpty = a_string is None or len(a_string.strip()) == 0
        return AssertionConcern.simple_handle_on_bool_val(
            aBool=isEmpty,
            exception=exception
            or self.__IllegalArgExceptionCls(
                f"String not empty: {a_message}",
                code=code or AssertionErrorCode.ARG_STRING_CANNOT_EMPTY.value,
                loc=loc,
            ),
        ).map(return_v(a_string))

    def assert_argument_not_equals(
        self,
        an_object1: object,
        an_object2: object,
        a_message: Optional[str] = None,
        exception: Optional[Exception] = None,
        loc: Optional[List[str]] = None,
        code: Optional[str] = None,
    ) -> Result:
        return AssertionConcern.simple_handle_on_bool_val(
            an_object1 == an_object2,
            exception
            or self.__IllegalArgExceptionCls(
                f"Argument cannot be equal: {a_message}",
                code=code or AssertionErrorCode.ARG_NOT_EQUALS.value,
                loc=loc,
            ),
        )

    def assert_argument_not_null(
        self,
        an_object: object,
        a_message: Optional[str] = None,
        exception: Optional[Exception] = None,
        loc: Optional[List[str]] = None,
        code: Optional[str] = None,
    ) -> Result:
        return AssertionConcern.simple_handle_on_bool_val(
            an_object is None,
            exception
            or self.__IllegalArgExceptionCls(
                f"Argument cannot be null: {a_message}",
                code=code or AssertionErrorCode.ARG_CANNOT_BE_NONE.value,
                loc=loc,
            ),
        ).map(return_v(an_object))

    def assert_argument_larger_than(
        self,
        a_value: Union[int, float],
        a_minium: Union[int, float],
        a_message: Optional[str] = None,
        exception: Optional[Exception] = None,
        loc: Optional[List[str]] = None,
        allow_equal: bool = False,
        code: Optional[str] = None,
    ) -> Result:
        return AssertionConcern.simple_handle_on_bool_val(
            (not allow_equal and a_value <= a_minium)
            or (allow_equal and a_value < a_minium),
            exception
            or self.__IllegalArgExceptionCls(
                f"Argument must be in larger than {a_minium} with {a_value}: {a_message} - loc: {loc}",
                code=code or AssertionErrorCode.ARG_NOT_LARGER_THAN.value,
                loc=loc,
            ),
        ).map(return_v(a_value))

    def assert_argument_smaller_than(
        self,
        a_value: Union[int, float],
        a_maximum: Union[int, float],
        a_message: Optional[str] = None,
        exception: Optional[Exception] = None,
        loc: Optional[List[str]] = None,
        allow_equal: bool = False,
        code: Optional[str] = None,
    ) -> Result:
        return AssertionConcern.simple_handle_on_bool_val(
            a_value >= a_maximum or (allow_equal and a_value > a_maximum),
            exception
            or self.__IllegalArgExceptionCls(
                f"Argument must be in smaller than {a_maximum}: {a_message} - loc: {loc}",
                code=code or AssertionErrorCode.ARG_NOT_SMALLER_THAN.value,
                loc=loc,
            ),
        ).map(return_v(a_value))

    @overload
    def assert_argument_range(
        self,
        a_value: int,
        a_minium: int,
        a_maximum: float,
        a_message: Optional[str] = None,
        exception: Optional[Exception] = None,
        loc: Optional[List[str]] = None,
    ) -> Result:
        ...

    @overload
    def assert_argument_range(
        self,
        a_value: float,
        a_minium: float,
        a_maximum: float,
        a_message: Optional[str] = None,
        exception: Optional[Exception] = None,
        loc: Optional[List[str]] = None,
        code: Optional[str] = None,
    ) -> Result:
        ...

    def assert_argument_range(
        self,
        a_value,
        a_minium,
        a_maximum,
        a_message=None,
        exception=None,
        loc=None,
        code=None,
    ):
        return AssertionConcern.simple_handle_on_bool_val(
            a_value < a_minium or a_value > a_maximum,
            exception
            or self.__IllegalArgExceptionCls(
                f"Value {a_value} just in range {a_minium} -> {a_maximum}: {a_message} - loc: {loc}",
                code=code or AssertionErrorCode.ARG_NOT_IN_RANGE.value,
                loc=loc,
            ),
        ).map(return_v(a_value))

    def assert_argument_regex(
        self,
        a_value: str,
        regex: str,
        a_message: Optional[str] = None,
        exception: Optional[Exception] = None,
        loc: Optional[List[str]] = None,
        code: Optional[str] = None,
    ) -> Result:
        return AssertionConcern.simple_handle_on_bool_val(
            re.match(regex, a_value) is None,
            exception
            or self.__IllegalArgExceptionCls(
                f"Argument does not match the required regex pattern: {a_message} with value {a_value} - loc: {loc}",
                code=code or AssertionErrorCode.ARG_NOT_REGEX_MATCHED.value,
                loc=loc,
            ),
        ).map(return_v(a_value))

    def assert_state_true(
        self,
        a_boolean: bool,
        a_message: Optional[str] = None,
        exception: Optional[Exception] = None,
        loc: Optional[List[str]] = None,
        code: Optional[str] = None,
    ):
        return AssertionConcern.simple_handle_on_bool_val(
            not a_boolean,
            exception
            or self.__IllegalStExceptionCls(
                a_message,
                code=code or AssertionErrorCode.STATE_NOT_SATISFIED.value,
                loc=loc,
            ),
        )

    def assert_state_false(
        self,
        aBoolean: bool,
        aMessage: Optional[str] = None,
        exception: Optional[Exception] = None,
        loc: Optional[List[str]] = None,
        code: Optional[str] = None,
    ):
        return AssertionConcern.simple_handle_on_bool_val(
            aBoolean,
            exception
            or self.__IllegalStExceptionCls(
                aMessage,
                code=code or AssertionErrorCode.STATE_CANNOT_STATISFIED.value,
                loc=loc,
            ),
        )

    def assert_future_maybe_not_nothing(
        self,
        future_maybe: Maybe,
        code: Optional[str] = None,
        a_message: Optional[str] = None,
        loc: Optional[List[str]] = [],
    ) -> FutureResult:
        match future_maybe:
            case Some(sth):
                return FutureSuccess(sth)
            case _:
                return FutureFailure(
                    self.__IllegalArgExceptionCls(code=code, message=a_message, loc=loc)
                )


class DomainAssertionConcern(AssertionConcern):
    __IllegalArgExceptionCls = DomainIllegalArgumentException
    __IllegalStExceptionCls = DomainIllegalStateException
