import asyncio
import traceback
from collections.abc import Callable, Iterable
from typing import Any, Coroutine, List, Optional, TypeVar

from alembic.context import execute
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


def forEach(function: Callable[[T, int], Any], iterable: Iterable[T]):
    for idx, element in enumerate(iterable):
        function(element, idx)


def mapToList(fn: Callable[[T], Any], items: List[T]) -> List[Any]:
    return flow(items, partial(map, fn), list)


def feedIdentity(obj):
    return lambda _: obj


def getClassName(obj):
    return obj.__class__.__name__


def setPrivateAttr(obj, field, value):
    setattr(obj, f"_{getClassName(obj)}__{field}", value)


def setPublicAttr(obj, field, value):
    setattr(obj, field, value)


def set_protected_attr(obj, field, value):
    setattr(obj, field, value)


InnerValueType = TypeVar("InnerValueType")


def maybeToFuture(v: InnerValueType) -> Future[Result[InnerValueType, Any]]:
    return flow(
        v,
        Maybe.from_optional,
        maybe_to_result,
        FutureResult.from_result,
        Future.from_future_result,
    )


def resultToFuture(v: Result[InnerValueType, Any]) -> FutureResult[InnerValueType, Any]:
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
            lash(returnFutureFailure(exception)),
            bind(FutureResult.from_value),
        )

    return checkNone


def checkNoneWithFutureWithException(
    exception: ExceptionType,
) -> Callable[[InnerValueType], FutureResult[InnerValueType, ExceptionType]]:
    return check_none_with_future_with_exception(exception)


def unwrapMaybe(v: Maybe[InnerValueType]) -> InnerValueType | None:
    return v.value_or(None)


def unwrap(v):
    return v.unwrap()


def assertFalse(exception):
    assert False


def assertTrue(value):
    assert True


@curry
def assertFalseWithDesc(desc, exception):
    assert False, desc or ""


@curry
def assertTrueWithDes(desc, value):
    assert True, desc or ""
    return True


@curry
def assertEqual(value, variable):
    assert variable == value


@curry
def assert_equal(value, variable):
    assert variable == value


def throwException(error):
    match error:
        case Exception():
            raise error
        case _:
            assert False


@future_safe
async def assertFutureResultSuccesful(result: FutureResult):
    ioResult = await result.awaitable()
    print("assertFutureResultSuccesful ", ioResult)
    assert is_successful(ioResult)
    result = flow(
        ioResult.unwrap(),
        unsafe_perform_io,
        # printResultWithText("assertFutureResultSuccesful result "),
    )
    return result


def raiseException(ex: Exception):
    traceback.print_exc()
    raise ex


def passTo(v: InnerValueType) -> Callable[[Any], InnerValueType]:
    return lambda _: v


def print_result_with_text(text: str):
    def printResult(v: InnerValueType) -> InnerValueType:
        print(f"{text} {v}")
        return v

    return printResult


def printResultWithText(text: str):
    return print_result_with_text(text)


def identityFactory(v: InnerValueType) -> Callable[[], InnerValueType]:
    def execute():
        return v

    return execute


def asyncToFutureResult(
    fnc: Callable[..., Coroutine[InnerValueType, Any, Any]],
) -> Callable[..., FutureResult[InnerValueType, Any]]:
    @future_safe
    async def execute(*args, **kwargs):
        result = await fnc(*args, **kwargs)
        return result

    return execute


def async_to_future_result(
    fnc: Callable[..., Coroutine[InnerValueType, Any, Any]],
) -> Callable[..., FutureResult[InnerValueType, Any]]:
    @future_safe
    async def execute(*args, **kwargs):
        result = await fnc(*args, **kwargs)
        return result

    return execute


def returnFutureFailure(
    e: ExceptionType,
) -> Callable[[Any], FutureResultE[ExceptionType]]:
    return lambda _: FutureResult.from_failure(e)


def unwrapFutureResultIO(result: IOResult[InnerValueType, Any]) -> InnerValueType:
    return unsafe_perform_io(unwrap(result))


def unwrap_future_result_io(result: IOResult[InnerValueType, Any]) -> InnerValueType:
    return unsafe_perform_io(unwrap(result))


def collectContainer(init):
    def withItems(items):
        return Fold.collect(items, init)

    return withItems


def filterNotNone(items: List[InnerValueType | None]) -> List[InnerValueType]:
    return list(filter(lambda item: item is not None, items))


def assertNotNone(v):
    print("assertNotNone", v)
    assert v is not None


def assertStateTrue(v):
    assert v


def feedArgs(func):
    return feed_args(func)


def feed_args(func):
    def execute(args: List[Any]):
        return func(*args)

    return execute


def feed_kwargs(func):
    def execute(kwargs: dict):
        return func(**kwargs)

    return execute


def feedKwargs(func):
    return feed_kwargs(func)


def throwFutureFailed(exception: Exception):
    return lambda _: FutureFailure(exception)


def not_nothing_or_throw_future_failed(
    exception: ExceptionType,
) -> Callable[[Maybe[InnerValueType]], FutureResult[InnerValueType, ExceptionType]]:
    def execute(
        value: Maybe[InnerValueType],
    ) -> FutureResult[InnerValueType, ExceptionType]:
        return flow(
            value,
            lash(throwFutureFailed(exception)),
            bind(lambda v: FutureResult.from_value(v)),
        )

    return execute


def notNoneOrThrowFutureFailed(
    exception: ExceptionType,
) -> Callable[[Maybe[InnerValueType]], FutureResult[InnerValueType, ExceptionType]]:
    return not_nothing_or_throw_future_failed(exception)


def unwrapFutureIOMaybe(
    value: IOResult[Maybe[InnerValueType], Any]
) -> InnerValueType | None:
    return unwrapMaybe(unsafe_perform_io(unwrap(value)))


def returnV(v: InnerValueType) -> Callable[[Any], InnerValueType]:
    return lambda _: v


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


def tap_excute_future(fn: Callable[[T], FutureResult]):
    def execute(input: T) -> FutureResult:
        return fn(input).map(return_v(input))

    return execute


def tap_failure_execute_future(fn: Callable[[T], FutureResult]):
    def execute(input: T) -> FutureResult:
        return fn(input).bind(return_v(FutureFailure(input)))

    return execute
