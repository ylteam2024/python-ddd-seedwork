import asyncio
import traceback
from collections.abc import Callable, Iterable
from typing import Any, Coroutine, List, Optional, TypeVar

from returns.converters import maybe_to_result
from returns.curry import curry, partial
from returns.future import (Future, FutureFailure, FutureResult, FutureResultE,
                            future_safe)
from returns.io import IOResult
from returns.iterables import Fold
from returns.maybe import Maybe
from returns.pipeline import flow, is_successful
from returns.pointfree import bind, lash
from returns.result import Result
from returns.unsafe import unsafe_perform_io

T = TypeVar("T")

ExceptionType = TypeVar("ExceptionType", bound=Exception)

__all__ = [
    "apply",
    "assert_equal",
    "assert_false",
    "assert_false_with_desc",
    "assert_future_result_succesful",
    "assert_not_none",
    "assert_state_true",
    "assert_true",
    "assert_true_with_des",
    "async_to_future_result",
    "check_none_with_future_with_exception",
    "collect_container",
    "execute",
    "feed_args",
    "feed_identity",
    "feed_kwargs",
    "filter_not_none",
    "for_each",
    "identity_factory",
    "map_to_list",
    "maybe_to_future",
    "not_nothing_or_throw_future_failed",
    "pass_to",
    "print_result_with_text",
    "raise_exception",
    "result_to_future",
    "return_future_failure",
    "set_private_attr",
    "set_protected_attr",
    "set_public_attr",
    "tap_excute_future",
    "tap_failure_execute_future",
    "throw_exception",
    "throw_future_failed",
    "unsafe_panic",
    "unwrap",
    "unwrap_future_io_maybe",
    "unwrap_future_result_io",
    "unwrap_maybe",
    "return_v",
]


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


def maybe_to_future(v: InnerValueType) -> Future[Result[InnerValueType, Any]]:
    return flow(
        v,
        Maybe.from_optional,
        maybe_to_result,
        FutureResult.from_result,
        Future.from_future_result,
    )


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
    return v.unwrap()


def assert_false(exception):
    assert False


def assert_true(value):
    assert True


@curry
def assert_false_with_desc(desc, exception):
    assert False, desc or ""


@curry
def assert_true_with_des(desc, value):
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


def collect_container(init):
    def with_items(items):
        return Fold.collect(items, init)

    return with_items


def filter_not_none(items: List[InnerValueType | None]) -> List[InnerValueType]:
    return list(filter(lambda item: item is not None, items))


def assert_not_none(v):
    print("assertNotNone", v)
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


def not_nothing_or_throw_future_failed(
    exception: ExceptionType,
) -> Callable[[Maybe[InnerValueType]], FutureResult[InnerValueType, ExceptionType]]:
    def execute(
        value: Maybe[InnerValueType],
    ) -> FutureResult[InnerValueType, ExceptionType]:
        return flow(
            value,
            lash(throw_future_failed(exception)),
            bind(lambda v: FutureResult.from_value(v)),
        )

    return execute


def unwrap_future_io_maybe(
    value: IOResult[Maybe[InnerValueType], Any]
) -> InnerValueType | None:
    return unwrap_maybe(unsafe_perform_io(unwrap(value)))


def return_v(v: InnerValueType) -> Callable[[Any], InnerValueType]:
    return lambda _: v


FunctionType = TypeVar("FunctionType", bound=Callable)


def apply(f: Callable, *args, **kwargs):
    return lambda _: f(*args, **kwargs)


def unsafe_panic(f: Callable[..., Result | FutureResult]):
    def wrapper(*args, **kwargs):
        result = unwrap(f(*args, **kwargs))
        return result

    return wrapper


def execute(fn: Optional[Callable[..., T]], *args, **kwargs) -> T | None:
    match fn:
        case Callable():
            return fn(*args, **kwargs)
        case _:
            return None


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


def tap_failure_execute_future(
    fn: Callable[[T], FutureResultE]
) -> Callable[[T], FutureResultE]:
    def execute(input: T) -> FutureResultE:
        return fn(input).bind(return_v(FutureFailure(input)))

    return execute
