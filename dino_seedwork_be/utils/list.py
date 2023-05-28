from collections.abc import Callable
from typing import List, Set, TypeVar

from returns.maybe import Maybe

__all__ = ["remove_none", "unique", "shallow_compare_list"]


def remove_none(aList: List) -> List:
    return list(filter(lambda a: a is not None, aList))


def unique(a_list: List) -> List:
    return list(set(a_list))


def shallow_compare_list(a1: List, a2: List):
    return not any((item not in a2) for item in a1)


T = TypeVar("T")


def get_one(condition: Callable[[T], bool], l: List[T] | Set[T]) -> Maybe[T]:
    return Maybe.from_optional(next((v for v in l if condition(v)), None))
