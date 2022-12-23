from functools import reduce
from typing import Generic, Iterable, List, TypeVar

__all__ = ["DuplicateKeyError", "ValidateSet", "set_add", "set_remove", "set_from"]


class DuplicateKeyError(Exception):
    pass


ItemType = TypeVar("ItemType")


class ValidateSet(set[ItemType], Generic[ItemType]):
    def __init__(self, val: Iterable[ItemType]):
        super().__init__(val)

    def add(self, value):
        if value in self:
            raise DuplicateKeyError("Value {!r} already present".format(value))
        super().add(value)

    def update(self, values):
        error_values = []
        for value in values:
            if value in self:
                error_values.append(value)
        if error_values:
            raise DuplicateKeyError(
                "Value(s) {!r} already present".format(error_values)
            )
        super().update(values)

    def copy(self):
        return ValidateSet(super().copy())


def set_add(s, x):
    return len(s) != (s.add(x) or len(s))


def set_remove(s, x):
    try:
        s.remove(x)
        return True
    except KeyError:
        return False


def set_from(listItem: List):
    def reduce_func(acc: ValidateSet, item):
        new_set = acc.copy()
        new_set.add(item)
        return new_set

    return reduce(reduce_func, listItem, ValidateSet([]))
