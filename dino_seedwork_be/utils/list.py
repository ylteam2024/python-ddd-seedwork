from typing import List

__all__ = ["remove_none"]


def remove_none(aList: List) -> List:
    return list(filter(lambda a: a is not None, aList))
