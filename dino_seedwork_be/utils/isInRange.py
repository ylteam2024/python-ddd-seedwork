from typing import overload


@overload
def isInRange(aValue: int, aMinimum: int, aMaximum: int) -> bool:
    ...


@overload
def isInRange(aValue: float, aMinimum: float, aMaximum: float) -> bool:
    ...


def isInRange(aValue, aMinimum, aMaximum):
    return aValue >= aMinimum and aValue <= aMaximum
