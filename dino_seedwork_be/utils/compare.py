from typing import List, TypeVar

ElementType = TypeVar("ElementType")


def shallowCompareList(a1: List, a2: List):
    return not any((item not in a2) for item in a1)
