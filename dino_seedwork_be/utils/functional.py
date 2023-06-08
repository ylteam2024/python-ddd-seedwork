import asyncio
import traceback
from collections.abc import Callable, Iterable
from typing import Any, Coroutine, List, Optional, ParamSpec, TypeVar

from returns.converters import maybe_to_result
from returns.curry import curry, partial
from returns.functions import identity
from returns.future import (Future, FutureFailure, FutureResult, FutureResultE,
                            FutureSuccess, future_safe)
from returns.io import IOFailure, IOResult, IOSuccess
from returns.iterables import Fold
from returns.maybe import Maybe
from returns.pipeline import flow, is_successful
from returns.pointfree import bind, lash
from returns.primitives.exceptions import UnwrapFailedError
from returns.result import Failure, Result, Success
from returns.unsafe import unsafe_perform_io

from dino_seedwork_be.exceptions import MainException

T = TypeVar("T")

ExceptionType = TypeVar("ExceptionType", bound=Exception)


def for_each(function: Callable[[T, int], Any], iterable: Iterable[T]):
    for idx, element in enumerate(iterable):
        function(element, idx)


def map_to_list(fn: Callable[[T], Any], items: List[T]) -> List[Any]:
    return flow(items, partial(map, fn), list)


def feed_identity(obj):
    return lambda _: obj


def get_class_name(obj):
    return obj.__class__.__name__


def set_private_attr(obj, field, value):
    setattr(obj, f"_{get_class_name(obj)}__{field}", value)


def set_public_attr(obj, field, value):
    setattr(obj, field, value)


def set_protected_attr(obj, field, value):
    setattr(obj, field, value)


InnerValueType = TypeVar("InnerValueType")


def maybe_to_future(exception: MainException):
    def convert(v: Maybe[InnerValueType]) -> FutureResult[InnerValueType, Any]:
        return flow(v, bind(FutureSuccess), lash(lambda _: FutureFailure(exception)))

    return convert


def maybe_to_result(exception: MainException):
    def convert(v: Maybe[InnerValueType]) -> Result[InnerValueType, Any]:
        return flow(v, bind(Success), lash(lambda _: Failure(exception)))

    return convert


def result_to_future(
    v: Result[InnerValueType, Any]
) -> FutureResult[InnerValueType, Any]:
    result = flow(v, FutureResult.from_result)
    return result


def check_none_with_future_with_exception(
    exception: ExceptionType,
) -> Callable[[InnerValueType], FutureResult[InnerValueType, ExceptionType]]:
    def checkNone(
        v: InnerValueType,
    ) -> FutureResult[InnerValueType, ExceptionType]:
        return flow(
            v,
            Maybe.from_optional,
            lash(return_future_failure(exception)),
            bind(FutureResult.from_value),
        )

    return checkNone


def unwrap_maybe(v: Maybe[InnerValueType]) -> InnerValueType | None:
    return v.value_or(None)


def unwrap(v):
    try:
        return v.unwrap()
    except UnwrapFailedError as error:
        raise error.halted_container._inner_value


def assert_false(_):
    assert False


def assert_true(_):
    assert True


@curry
def assert_false_with_desc(desc):
    assert False, desc or ""


@curry
def assert_true_with_des(desc):
    assert True, desc or ""
    return True


@curry
def assert_equal(value, variable):
    assert variable == value


def throw_exception(error):
    match error:
        case Exception():
            raise error
        case _:
            assert False


@future_safe
async def assert_future_result_succesful(result: FutureResult):
    ioResult = await result.awaitable()
    assert is_successful(ioResult)
    result = flow(
        ioResult.unwrap(),
        unsafe_perform_io,
        # printResultWithText("assertFutureResultSuccesful result "),
    )
    return result


def raise_exception(ex: Exception):
    traceback.print_exc()
    raise ex


def pass_to(v: InnerValueType) -> Callable[[Any], InnerValueType]:
    return lambda _: v


def print_result_with_text(text: str):
    def printResult(v: InnerValueType) -> InnerValueType:
        print(f"{text} {v}")
        return v

    return printResult


def identity_factory(v: InnerValueType) -> Callable[[], InnerValueType]:
    def execute():
        return v

    return execute


def async_to_future_result(
    fnc: Callable[..., Coroutine[InnerValueType, Any, Any]],
) -> Callable[..., FutureResult[InnerValueType, Any]]:
    @future_safe
    async def execute(*args, **kwargs):
        result = await fnc(*args, **kwargs)
        return result

    return execute


def return_future_failure(
    e: ExceptionType,
) -> Callable[[Any], FutureResultE[ExceptionType]]:
    return lambda _: FutureResult.from_failure(e)


def unwrap_future_result_io(result: IOResult[InnerValueType, Any]) -> InnerValueType:
    return unsafe_perform_io(unwrap(result))


_ValueType = TypeVar("_ValueType", covariant=True)


async def unwrap_future_result(
    future_result: FutureResult[_ValueType, Any]
) -> _ValueType:
    io_result = await future_result.awaitable()
    match io_result:
        case IOSuccess(Success(data)):
            return data
        case IOSuccess(Failure(e)):
            raise e
        case IOFailure(Failure(e)):
            raise e
        case _:
            raise MainException("UNKNOW_PATTERN")


def collect_container(init):
    def with_items(items):
        return Fold.collect(items, init)

    return with_items


def filter_not_none(items: List[InnerValueType | None]) -> List[InnerValueType]:
    return list(filter(lambda item: item is not None, items))


def assert_not_none(v):
    assert v is not None


def assert_state_true(v):
    assert v


def feed_args(func):
    def execute(args: List[Any]):
        return func(*args)

    return execute


def feed_kwargs(func):
    def execute(kwargs: dict):
        return func(**kwargs)

    return execute


def throw_future_failed(exception: Exception):
    return lambda _: FutureFailure(exception)


def print_exception_with_traceback(exception: Exception):
    return traceback.print_tb(exception.__traceback__)


def unwrap_future_io_maybe(
    value: IOResult[Maybe[InnerValueType], Any]
) -> InnerValueType | None:
    return unwrap_maybe(unsafe_perform_io(unwrap(value)))


def return_v(v: InnerValueType) -> Callable[[Any], InnerValueType]:
    return lambda _: v


FunctionType = TypeVar("FunctionType", bound=Callable)

P = ParamSpec("P")
T = TypeVar("T")


def apply(
    f: Callable[P, T],
    *args: P.args,
    **kwargs: P.kwargs,
) -> Callable[[Any], T]:
    return lambda _: f(*args, **kwargs)


def unsafe_panic(f: Callable[..., Result | FutureResult]):
    def wrapper(*args, **kwargs):
        result = unwrap(f(*args, **kwargs))
        return result

    return wrapper


def execute(fn: Optional[Callable[..., T]], *args, **kwargs) -> T | None:
    return Maybe.from_optional(fn).map(lambda f: f(*args, **kwargs)).value_or(None)


def async_execute(fn: Callable[..., FutureResult]):
    def _(*args, **kwargs):
        return asyncio.run(fn(*args, **kwargs).awaitable())

    return _


def tap_excute_future(
    fn: Callable[[T], FutureResult]
) -> Callable[[T], FutureResult[T, Any]]:
    def execute(input: T) -> FutureResult[T, Any]:
        return fn(input).map(return_v(input))

    return execute


T1 = TypeVar("T1")
E = TypeVar("E", bound=MainException)


def tap_result(fn: Callable[[T], Result[T1, E]]) -> Callable[[T], Result[T, E]]:
    def execute(input: T) -> Result[T, E]:
        return fn(input).map(return_v(input))

    return execute


def tap_failure_execute_future(
    fn: Callable[[T], FutureResultE]
) -> Callable[[T], FutureResultE]:
    def execute(input: T) -> FutureResultE:
        return fn(input).bind(return_v(FutureFailure(input)))

    return execute


def must_be_true(
    exception: Optional[MainException] = None,
) -> Callable[[bool], Result]:
    def assert_true(value: bool) -> Result:
        has_value_and_exception = value is False and exception is not None
        match has_value_and_exception:
            case True:
                return Failure(exception)
            case False:
                return Success(value)

    return assert_true


def result_to_future_callable(fn: Callable[..., Result]):
    return lambda *args, **kwargs: FutureResult.from_result(fn(*args, **kwargs))


RE = TypeVar("RE", bound=MainException)


def tap_result_from_future(
    fn: Callable[[T], Result[T1, E]], err: Callable[[MainException], RE] = identity
) -> Callable[[T], FutureResult[T, RE]]:
    def execute(input: T) -> FutureResult[T, RE]:
        match fn(input):
            case Success():
                return FutureSuccess(input)
            case Failure(e):
                return FutureFailure(err(e))
            case _:
                return FutureFailure(err(MainException(code="UNKNOW_RESULT")))

    return execute


def with_default_value(original: Optional[T], defaultValue: T) -> T:
    return original or defaultValue
