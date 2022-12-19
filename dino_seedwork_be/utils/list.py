from typing import List


def remove_none(aList: List) -> List:
    return list(filter(lambda a: a is not None, aList))
