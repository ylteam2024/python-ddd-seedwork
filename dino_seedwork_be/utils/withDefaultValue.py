from typing import Optional, TypeVar

T = TypeVar("T")


def withDefaultValue(original: Optional[T], defaultValue: T) -> T:
    return original or defaultValue
