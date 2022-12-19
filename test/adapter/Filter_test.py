from typing import List, TypedDict

from dino_seedwork_be.adapters.rest import (Filter, ParamOperators,
                                            ParamWithComparing)


class PlainFilter(TypedDict):
    population: List[str] | str
    size: List[str] | str


class TestFilter:
    def test_parseFilters(self):
        filter = Filter(
            {
                "population": ["~gt~100000", "~lt~500000"],
                "size": "~eq~100000",
            }
        )
        parsedFilter = filter.parsed_filter
        assert parsedFilter["population"] is not None
        assert isinstance(parsedFilter["population"], List)
        assert parsedFilter["population"][0] == ParamWithComparing(
            operator=ParamOperators.GT, value=100000
        )
        assert parsedFilter["population"][1] == ParamWithComparing(
            operator=ParamOperators.LT, value=500000
        )
        assert parsedFilter["size"] == ParamWithComparing(
            operator=ParamOperators.EQ, value=100000
        )
