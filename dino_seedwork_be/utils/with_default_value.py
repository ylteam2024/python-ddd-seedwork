from typing import Optional, TypeVar

T = TypeVar("T")

__all__ = ["with_default_value"]


def with_default_value(original: Optional[T], defaultValue: T) -> T:
    return original or defaultValue
