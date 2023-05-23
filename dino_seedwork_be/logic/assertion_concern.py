import re
from enum import Enum
from typing import Any, List, TypeVar, Union

from returns.future import FutureFailure, FutureResult, FutureSuccess
from returns.iterables import Fold
from returns.maybe import Maybe, Nothing, Some
from returns.pipeline import flow
from returns.pointfree import alt
from returns.result import Result, Success

from dino_seedwork_be.exceptions import (IllegalArgumentException,
                                         IllegalStateException, MainException)
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


InputType = TypeVar("InputType")


class AssertionConcern:
    IllegalArgExceptionCls = IllegalArgumentException
    IllegalStExceptionCls = IllegalStateException

    @staticmethod
    def simple_handle_on_bool_val(a_bool: bool, exception: Maybe[Exception] = Nothing):
        """
        Throw if a_bool is True
        """
        match a_bool:
            case True:
                return Result.from_failure(exception.value_or(MainException()))
        return Result.from_value("OK")

    def assert_argument_equals(
        self,
        a_message: Maybe[str] = Nothing,
        exception: Maybe[Exception] = Nothing,
        loc: Maybe[List[str]] = Nothing,
        code: Maybe[str] = Nothing,
        an_obj1: object = None,
        an_obj2: object = None,
    ) -> Result:
        is_not_equal = an_obj1 != an_obj2
        return AssertionConcern.simple_handle_on_bool_val(
            is_not_equal,
            exception
            or self.IllegalArgExceptionCls(
                message=a_message.value_or(""),
                code=code.value_or(AssertionErrorCode.ARG_SHOULD_EQUALS.value),
                loc=loc.value_or([]),
            ),
        )

    def assert_argument_false(
        self,
        a_boolean: bool,
        a_message: Maybe[str] = Nothing,
        exception: Maybe[Exception] = Nothing,
        loc: Maybe[List[str]] = Nothing,
        code: Maybe[str] = Nothing,
    ) -> Result:
        is_false = not a_boolean
        return AssertionConcern.simple_handle_on_bool_val(
            not is_false,
            exception
            or self.IllegalArgExceptionCls(
                f"Must be False: {a_message.value_or('')}",
                code=code.value_or(AssertionErrorCode.ARG_CANNOT_BE_TRUE.value),
                loc=loc.value_or([]),
            ),
        )

    def assert_argument_true(
        self,
        a_boolean: bool,
        a_message: Maybe[str] = Nothing,
        exception: Maybe[Exception] = Nothing,
        loc: Maybe[List[str]] = Nothing,
        code: Maybe[str] = Nothing,
    ) -> Result:
        is_true = a_boolean
        return AssertionConcern.simple_handle_on_bool_val(
            not is_true,
            exception
            or self.IllegalArgExceptionCls(
                f"Must be True: {a_message.value_or('')}",
                code=code.value_or(AssertionErrorCode.ARG_CANNOT_BE_FALSE.value),
                loc=loc.value_or([]),
            ),
        )

    def assert_argument_length(
        self,
        a_string: str,
        a_minimum: int,
        a_maximum: int,
        a_message: Maybe[str] = Nothing,
        exception: Maybe[Exception] = Nothing,
        loc: Maybe[List[str]] = Nothing,
        code: Maybe[str] = Nothing,
    ) -> Result:
        length = len(a_string.strip())
        match length > a_maximum:
            case True:
                return Result.from_failure(
                    exception
                    or self.IllegalArgExceptionCls(
                        f"Length must be less than {a_maximum} but {a_string} is not: {a_message}",
                        code=code.value_or(AssertionErrorCode.ARG_LENGTH_INVALID.value),
                        loc=loc.value_or([]),
                    ),
                )

        match length < a_minimum:
            case True:
                return Result.from_failure(
                    exception
                    or self.IllegalArgExceptionCls(
                        f"Length must be large than {a_minimum}: {a_message}",
                        code=code.value_or(AssertionErrorCode.ARG_LENGTH_INVALID.value),
                        loc=loc.value_or([]),
                    )
                )
        return Success(a_string)

    def assert_argument_not_empty(
        self,
        a_string: Maybe[str],
        a_message: Maybe[str] = Nothing,
        exception: Maybe[Exception] = Nothing,
        loc: Maybe[List[str]] = Nothing,
        code: Maybe[str] = Nothing,
    ) -> Result:
        is_empty = a_string.map(
            lambda a_string: a_string is None or len(a_string.strip()) == 0
        ).value_or(False)
        return AssertionConcern.simple_handle_on_bool_val(
            a_bool=is_empty,
            exception=exception
            or self.IllegalArgExceptionCls(
                f"String not empty: {a_message.value_or('')}",
                code=code.value_or(AssertionErrorCode.ARG_STRING_CANNOT_EMPTY.value),
                loc=loc.value_or([]),
            ),
        ).map(return_v(a_string))

    def assert_argument_not_equals(
        self,
        an_object1: object,
        an_object2: object,
        a_message: Maybe[str] = Nothing,
        exception: Maybe[Exception] = Nothing,
        loc: Maybe[List[str]] = Nothing,
        code: Maybe[str] = Nothing,
    ) -> Result:
        return AssertionConcern.simple_handle_on_bool_val(
            an_object1 == an_object2,
            exception
            or self.IllegalArgExceptionCls(
                f"Argument cannot be equal: {a_message}",
                code=code.value_or(AssertionErrorCode.ARG_NOT_EQUALS.value),
                loc=loc.value_or([]),
            ),
        )

    def assert_argument_not_null(
        self,
        an_object: InputType,
        a_message: Maybe[str] = Nothing,
        exception: Maybe[Exception] = Nothing,
        loc: Maybe[List[str]] = Nothing,
        code: Maybe[str] = Nothing,
    ) -> Result[InputType, Any]:
        return AssertionConcern.simple_handle_on_bool_val(
            an_object is None,
            exception
            or self.IllegalArgExceptionCls(
                f"Argument cannot be null: {a_message}",
                code=code.value_or(AssertionErrorCode.ARG_CANNOT_BE_NONE.value),
                loc=loc.value_or([]),
            ),
        ).map(return_v(an_object))

    def assert_argument_larger_than(
        self,
        a_value: Union[int, float],
        a_minium: Union[int, float],
        a_message: Maybe[str] = Nothing,
        exception: Maybe[Exception] = Nothing,
        loc: Maybe[List[str]] = Nothing,
        allow_equal: bool = False,
        code: Maybe[str] = Nothing,
    ) -> Result:
        return AssertionConcern.simple_handle_on_bool_val(
            (not allow_equal and a_value <= a_minium)
            or (allow_equal and a_value < a_minium),
            exception.lash(
                return_v(
                    Some(
                        self.IllegalArgExceptionCls(
                            f"Argument must be in larger than {a_minium} with {a_value}: {a_message} - loc: {loc}",
                            code=code.value_or(
                                AssertionErrorCode.ARG_NOT_LARGER_THAN.value
                            ),
                            loc=loc.value_or([]),
                        )
                    )
                )
            ),
        ).map(return_v(a_value))

    def assert_argument_smaller_than(
        self,
        a_value: Union[int, float],
        a_maximum: Union[int, float],
        a_message: Maybe[str] = Nothing,
        exception: Maybe[Exception] = Nothing,
        loc: Maybe[List[str]] = Nothing,
        allow_equal: bool = False,
        code: Maybe[str] = Nothing,
    ) -> Result:
        return AssertionConcern.simple_handle_on_bool_val(
            a_value >= a_maximum or (allow_equal and a_value > a_maximum),
            exception
            or self.IllegalArgExceptionCls(
                f"Argument must be in smaller than {a_maximum}: {a_message} - loc: {loc}",
                code=code.value_or(AssertionErrorCode.ARG_NOT_SMALLER_THAN.value),
                loc=loc.value_or([]),
            ),
        ).map(return_v(a_value))

    def assert_argument_range(
        self,
        a_value: float,
        a_minium: float,
        a_maximum: float,
        a_message: Maybe[str] = Nothing,
        exception: Maybe[Exception] = Nothing,
        loc: Maybe[List[str]] = Nothing,
        code: Maybe[str] = Nothing,
    ) -> Result:
        return AssertionConcern.simple_handle_on_bool_val(
            a_value < a_minium or a_value > a_maximum,
            exception
            or self.IllegalArgExceptionCls(
                f"Value {a_value} just in range {a_minium} -> {a_maximum}: {a_message} - loc: {loc}",
                code=code.value_or(AssertionErrorCode.ARG_NOT_IN_RANGE.value),
                loc=loc.value_or([]),
            ),
        ).map(return_v(a_value))

    def assert_argument_regex(
        self,
        a_value: str,
        regex: str,
        a_message: Maybe[str] = Nothing,
        exception: Maybe[Exception] = Nothing,
        loc: Maybe[List[str]] = Nothing,
        code: Maybe[str] = Nothing,
    ) -> Result:
        return AssertionConcern.simple_handle_on_bool_val(
            re.match(regex, a_value) is None,
            exception.lash(
                return_v(
                    Some(
                        self.IllegalArgExceptionCls(
                            f"Argument does not match the required regex pattern: {a_message} with value {a_value} - loc: {loc}",
                            code=code.value_or(
                                AssertionErrorCode.ARG_NOT_REGEX_MATCHED.value
                            ),
                            loc=loc.value_or([]),
                        )
                    )
                )
            ),
        ).map(return_v(a_value))

    def assert_state_true(
        self,
        a_boolean: bool,
        a_message: Maybe[str] = Nothing,
        exception: Maybe[Exception] = Nothing,
        loc: Maybe[List[str]] = Nothing,
        code: Maybe[str] = Nothing,
    ):
        return AssertionConcern.simple_handle_on_bool_val(
            not a_boolean,
            exception
            or self.IllegalStExceptionCls(
                a_message.value_or(""),
                code=code.value_or(AssertionErrorCode.STATE_NOT_SATISFIED.value),
                loc=loc.value_or([]),
            ),
        )

    def assert_state_false(
        self,
        a_boolean: bool,
        a_message: Maybe[str] = Nothing,
        exception: Maybe[Exception] = Nothing,
        loc: Maybe[List[str]] = Nothing,
        code: Maybe[str] = Nothing,
    ):
        return AssertionConcern.simple_handle_on_bool_val(
            a_boolean,
            exception
            or self.IllegalStExceptionCls(
                a_message.value_or(""),
                code=code.value_or(AssertionErrorCode.STATE_CANNOT_STATISFIED.value),
                loc=loc.value_or([]),
            ),
        )

    def assert_future_maybe_not_nothing(
        self,
        future_maybe: Maybe,
        code: Maybe[str] = Nothing,
        a_message: Maybe[str] = Nothing,
        loc: Maybe[List[str]] = Nothing,
    ) -> FutureResult:
        match future_maybe:
            case Some(sth):
                return FutureSuccess(sth)
            case _:
                return FutureFailure(
                    self.IllegalArgExceptionCls(
                        code=code.value_or(AssertionErrorCode.ARG_CANNOT_BE_NONE.value),
                        message=a_message.value_or(""),
                        loc=loc.value_or([]),
                    )
                )

    def assert_all_not_nothing(
        self,
        a_list: List[Maybe],
        code: Maybe = Nothing,
        a_message: Maybe = Nothing,
        loc: Maybe[List[str]] = Nothing,
    ):
        return flow(
            map(lambda an_item: self.assert_future_maybe_not_nothing(an_item), a_list),
            lambda iter: Fold.collect(iter, Success(())),
            alt(
                return_v(
                    self.IllegalArgExceptionCls(
                        message=a_message.value_or(""),
                        code=code.value_or("ERROR"),
                        loc=loc.value_or([]),
                    )
                )
            ),
        )
