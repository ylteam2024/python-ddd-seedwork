from typing import Callable, TypeVar

from returns.maybe import Maybe, Some
from returns.result import Result, Success

from dino_seedwork_be.domain.exceptions import DomainException

from .domain_safe import domain_safe
from .list import to_list

InnerValue = TypeVar("InnerValue")
ResultValue = TypeVar("ResultValue")


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


__all__ = ["to_list", "domain_safe", "handle_on_maybe"]
