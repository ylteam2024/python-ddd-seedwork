from typing import overload

__all__ = ["is_in_range"]


@overload
def is_in_range(a_value: int, a_minimum: int, a_maximum: int) -> bool:
    ...


@overload
def is_in_range(a_value: float, a_minimum: float, a_maximum: float) -> bool:
    ...


def is_in_range(a_value, a_minimum, a_maximum):
    return a_value >= a_minimum and a_value <= a_maximum
