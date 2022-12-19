import json
import re
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from functools import reduce
from typing import (Any, Dict, Generic, List, Literal, Optional, TypedDict,
                    TypeVar)

from pydantic import BaseModel
from returns.maybe import Maybe, Nothing, Some
from toolz.dicttoolz import assoc

from dino_seedwork_be.domain.value_objects import ValueObject
from dino_seedwork_be.exceptions import MainException
from dino_seedwork_be.utils.text import parse_num_or_keeping

DataType = TypeVar("DataType")


class RestPayload(Generic[DataType], BaseModel):
    data: DataType
    _link: dict


def to_rest_payload(data: object | str = "OK", link: dict = {}):
    return {"data": data, "_link": link}


def pagination(total: int, offset: int, limit: int, items: list):
    return {
        "items": items,
        "offset": offset,
        "limit": limit,
        "total": total,
    }


def field_error_valition(loc: List[str], msg: str, type: Optional[str]):
    return {"loc": loc, msg: str, type: type}


def error_validation(detail: dict | List):
    return {"validation": detail}


def error_validation_standard(exception: MainException):
    return {
        "validation": [
            {
                "loc": exception.loc().value_or(None),
                "code": exception.code().value_or(None),
                "message": exception.message().value_or(None),
            }
        ]
    }


def error_detail_with_code_standard(exception: MainException):
    return {
        "origin": "DINO_MARKET_BACKEND",
        "code": exception.code(),
        "message": exception.message(),
        "loc": exception.loc(),
    }


def error_detail_with_code(exception: MainException, is_validation: bool = False):
    message = {}
    try:
        message = json.loads(exception.message().value_or("{}"))
    except Exception:
        pass
    return {
        "origin": "DINO_MARKET_BACKEND",
        "code": exception.code(),
        "validation" if is_validation else "message": message,
    }


EntityAttrsType = TypeVar("EntityAttrsType", bound=TypedDict)


class FilterWithPag(Generic[EntityAttrsType]):
    filters: EntityAttrsType
    order: Dict[str, Literal["ASC", "DESC"]]
    offset: int
    limit: int


@dataclass
class ParamOperator(ValueObject):
    symbol: str

    def __eq__(self, __o: object) -> bool:
        match __o:
            case ParamOperator():
                return self.symbol == __o.symbol
            case _:
                return False

    def __hash__(self) -> int:
        return hash(self.symbol)

    def is_lt(self):
        return self.symbol == "lt"

    def is_lte(self):
        return self.symbol == "lte"

    def is_gt(self):
        return self.symbol == "gt"

    def is_gte(self):
        return self.symbol == "gte"

    def is_eq(self):
        return self.symbol == "eq"


class ParamOperators(Enum):
    LT = ParamOperator("lt")
    LTE = ParamOperator("lte")
    GT = ParamOperator("gt")
    GTE = ParamOperator("gte")
    EQ = ParamOperator("eq")


@dataclass
class ParamWithComparing:
    operator: ParamOperators
    value: str | int | float | datetime

    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, ParamWithComparing):
            return __o.operator == self.operator and __o.value == self.value
        return False


FilterElement = Any | ParamWithComparing | List[Any] | List[ParamWithComparing]

PlainFilterSet = Dict[str, Any]

FilterSet = Dict[str, FilterElement]


class Filter:
    parsed_filter: FilterSet
    filters: PlainFilterSet
    order: Dict[str, Literal["ASC", "DESC"]]
    q: Optional[str]

    def __init__(self, plainFilter: Dict[str, Any]) -> None:
        self.filters = plainFilter
        self.parsed_filter = self.parse_filters()
        super().__init__()

    def parse_filter(self, param_value: Any):
        def parse_a_instance(param_elem: Any):
            pattern = "~(.*?)~"
            pop_opr = (re.search(pattern, param_elem) or re.Match()).group(1)
            pop_no_str = re.sub(r"^~.*?~", "", param_elem)
            return ParamWithComparing(
                operator=ParamOperators(ParamOperator(pop_opr)),
                value=parse_num_or_keeping(pop_no_str),
            )

        try:
            match param_value:
                case list():
                    return list(map(lambda v: parse_a_instance(v), param_value))
                case _:
                    return parse_a_instance(param_value)
        except Exception as error:
            print("cannot parse ", error)
            return param_value

    def parse_filters(self):
        return reduce(
            lambda acc, key: assoc(acc, key, self.parse_filter(self.filters[key])),
            self.filters.keys(),
            {},
        )


class OrderParam(Enum):
    ASC = "ASC"
    DESC = "DESC"


def plain_order_to_param_order(plainOrder: Optional[str]) -> Maybe[OrderParam]:
    match plainOrder:
        case "asc":
            return Some(OrderParam.ASC)
        case "desc":
            return Some(OrderParam.DESC)
        case _:
            return Nothing


def to_param_orders(plainOrders: dict[str, Optional[str]]):
    return reduce(
        lambda acc, key: assoc(
            acc, key, plain_order_to_param_order(plainOrders[key]).value_or(None)
        ),
        plainOrders.keys(),
        {},
    )
