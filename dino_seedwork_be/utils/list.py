from typing import List

__all__ = ["remove_none", "unique", "shallow_compare_list"]


def remove_none(aList: List) -> List:
    return list(filter(lambda a: a is not None, aList))


def unique(a_list: List) -> List:
    return list(set(a_list))


def shallow_compare_list(a1: List, a2: List):
    return not any((item not in a2) for item in a1)
