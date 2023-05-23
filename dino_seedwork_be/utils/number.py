from typing import TypeVar, overload

NumberType = TypeVar("NumberType")

# Not pure
def increase(a_number: NumberType, amount: NumberType) -> NumberType:
    return a_number + amount


def negate(a_bool: bool) -> bool:
    return not a_bool


@overload
def is_in_range(a_value: int, a_minimum: int, a_maximum: int) -> bool:
    ...


@overload
def is_in_range(a_value: float, a_minimum: float, a_maximum: float) -> bool:
    ...


def is_in_range(a_value, a_minimum, a_maximum):
    return a_value >= a_minimum and a_value <= a_maximum
