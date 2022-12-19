from typing import Optional, TypeVar

T = TypeVar("T")


def with_default_value(original: Optional[T], defaultValue: T) -> T:
    return original or defaultValue
