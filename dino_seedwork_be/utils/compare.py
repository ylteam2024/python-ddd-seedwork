from typing import List, TypeVar

ElementType = TypeVar("ElementType")

__all__ = ["shallow_compare_list"]


def shallow_compare_list(a1: List, a2: List):
    return not any((item not in a2) for item in a1)
