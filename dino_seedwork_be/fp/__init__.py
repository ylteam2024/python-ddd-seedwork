from typing import Callable, Iterable, Tuple, TypeVar

from returns.future import FutureResult
from returns.iterables import Fold
from returns.maybe import Maybe, Some
from returns.result import Result, Success

from dino_seedwork_be.domain.exceptions import DomainException

from .domain_safe import domain_safe
from .list import to_list

InnerValue = TypeVar("InnerValue")
ResultValue = TypeVar("ResultValue")

_SecondType = TypeVar("_SecondType")
_ThirdType = TypeVar("_ThirdType")


def handle_on_maybe(
    handler: Callable[[InnerValue], Result[None, DomainException]]
) -> Callable[[Maybe[InnerValue]], Result[None, DomainException]]:
    def _handler(inner_value: Maybe[InnerValue]):
        match inner_value:
            case Some(v):
                return handler(v)
            case _:
                return Success(None)

    return _handler


def collect_result(
    iterable: Iterable[
        Result[_SecondType, _ThirdType],
    ],
    acc: Result[Tuple[_SecondType, ...], _ThirdType],
) -> Result[Tuple[_SecondType, ...], _ThirdType]:
    return Fold.collect(iterable, acc)


def collect_result_all(
    iterable: Iterable[
        Result[_SecondType, _ThirdType],
    ],
    acc: Result[Tuple[_SecondType, ...], _ThirdType],
) -> Tuple[Result[_SecondType, _ThirdType], ...]:
    return Fold.collect_all(iterable, acc)


def collect_fresult(
    iterable: Iterable[
        FutureResult[_SecondType, _ThirdType],
    ],
    acc: FutureResult[Tuple[_SecondType, ...], _ThirdType],
) -> FutureResult[Tuple[_SecondType, ...], _ThirdType]:
    return Fold.collect(iterable, acc)


def collect_fresult_all(
    iterable: Iterable[
        FutureResult[_SecondType, _ThirdType],
    ],
    acc: FutureResult[Tuple[_SecondType, ...], _ThirdType],
) -> FutureResult[Tuple[_SecondType, ...], _ThirdType]:
    return Fold.collect_all(iterable, acc)


__all__ = [
    "to_list",
    "domain_safe",
    "handle_on_maybe",
    "collect_result",
    "collect_result_all",
    "collect_fresult",
    "collect_fresult_all",
]
