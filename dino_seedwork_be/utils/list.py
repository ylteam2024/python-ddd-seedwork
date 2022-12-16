from typing import List


def removeNone(aList: List) -> List:
    return list(filter(lambda a: a is not None, aList))
