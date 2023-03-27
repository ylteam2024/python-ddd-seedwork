from typing import TypeVar

NumberType = TypeVar("NumberType")

__all__ = ["increase"]
# Not pure
def increase(a_number: NumberType, amount: NumberType) -> NumberType:
    return a_number + amount


def negate(a_bool: bool) -> bool:
    return not a_bool
