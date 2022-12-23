import json
from typing import Any, List, TypedDict, TypeVar

from dino_seedwork_be.adapters.rest import Filter
from dino_seedwork_be.utils.dict import extract

FilterType = TypeVar("FilterType", bound=TypedDict)

__all__ = ["Filters"]


class Filters:
    def __init__(self, keys: List[str]) -> None:
        self.keys = keys

    def __call__(self, filters: Any = {}):
        match filters:
            case str():
                try:
                    filters = json.loads(filters)
                except Exception as error:
                    filters = {}
        plain_filter = extract(filters, self.keys)
        return Filter(plain_filter).parsed_filter
