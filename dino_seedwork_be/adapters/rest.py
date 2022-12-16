import json
import re
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from functools import reduce
from typing import (Any, Dict, Generic, List, Literal, Optional, TypedDict,
                    TypeVar)

import jsonpickle
from pydantic import BaseModel
from returns.maybe import Maybe, Nothing, Some
from toolz.dicttoolz import assoc

from src.seedwork.domain.value_objects import ValueObject
from src.seedwork.exceptions import MainException
from src.seedwork.utils.meta import getLocalClassname
from src.seedwork.utils.text import parseNumOrKeeping

DataType = TypeVar("DataType")


class RestPayload(Generic[DataType], BaseModel):
    data: DataType
    _link: dict


def toJSONRestPayload(data: str | dict, link: dict = {}):
    match data:
        case str():
            return json.dumps({"data": jsonpickle.decode(data), "_link": link})
        case dict():
            return json.dumps({"data": data, "_link": link})


def toRestPayload(data: object | str = "OK", link: dict = {}):
    return to_rest_payload(data, link)


def to_rest_payload(data: object | str = "OK", link: dict = {}):
    return {"data": data, "_link": link}


def pagination(total: int, offset: int, limit: int, items: list):
    return {
        "items": items,
        "offset": offset,
        "limit": limit,
        "total": total,
    }


def fieldrrrorValition(loc: List[str], msg: str, type: Optional[str]):
    return {"loc": loc, msg: str, type: type}


def errorValidation(detail: dict | List):
    return {"validation": detail}


def errorValidationStandard(exception: MainException):
    return {
        "validation": [
            {
                "loc": exception.getLoc().value_or(None),
                "code": exception.getCode().value_or(None),
                "message": exception.getMessage().value_or(None),
            }
        ]
    }


def errorDetailWithCodeStandard(exception: MainException):
    return {
        "origin": "DINO_MARKET_BACKEND",
        "code": exception.getCode(),
        "message": exception.getMessage(),
        "loc": exception.getLoc(),
    }


def errorDetailWithCode(
    exception: Exception,
    detail: str,
    code: Optional[str] = None,
    isValidation: bool = False,
):
    message = detail
    try:
        message = json.loads(detail)
    except Exception:
        pass
    return {
        "origin": "DINO_MARKET_BACKEND",
        "code": code or getLocalClassname(exception),
        "validation" if isValidation else "message": message,
    }


def error_detail_with_code(exception: MainException, is_validation: bool = False):
    message = {}
    try:
        message = json.loads(exception.getMessage().value_or("{}"))
    except Exception:
        pass
    return {
        "origin": "DINO_MARKET_BACKEND",
        "code": exception.getCode(),
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

    def isLt(self):
        return self.symbol == "lt"

    def isLte(self):
        return self.symbol == "lte"

    def isGt(self):
        return self.symbol == "gt"

    def isGte(self):
        return self.symbol == "gte"

    def isEq(self):
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
    parsedFilter: FilterSet
    filters: PlainFilterSet
    order: Dict[str, Literal["ASC", "DESC"]]
    q: Optional[str]

    def __init__(self, plainFilter: Dict[str, Any]) -> None:
        self.filters = plainFilter
        self.parsedFilter = self.parseFilters()
        super().__init__()

    def parseFilter(self, paramValue: Any):
        def parseAInstance(paramElem: Any):
            pattern = "~(.*?)~"
            print("param Elem ", paramElem)
            pop_opr = (re.search(pattern, paramElem) or re.Match()).group(1)
            pop_no_str = re.sub(r"^~.*?~", "", paramElem)
            return ParamWithComparing(
                operator=ParamOperators(ParamOperator(pop_opr)),
                value=parseNumOrKeeping(pop_no_str),
            )

        try:
            match paramValue:
                case list():
                    return list(map(lambda v: parseAInstance(v), paramValue))
                case _:
                    return parseAInstance(paramValue)
        except Exception as error:
            print("cannot parse ", error)
            return paramValue

    def parseFilters(self):
        return reduce(
            lambda acc, key: assoc(acc, key, self.parseFilter(self.filters[key])),
            self.filters.keys(),
            {},
        )


class OrderParam(Enum):
    ASC = "ASC"
    DESC = "DESC"


def plainOrderToParamOrder(plainOrder: Optional[str]) -> Maybe[OrderParam]:
    match plainOrder:
        case "asc":
            return Some(OrderParam.ASC)
        case "desc":
            return Some(OrderParam.DESC)
        case _:
            return Nothing


def toParamOrders(plainOrders: dict[str, Optional[str]]):
    return reduce(
        lambda acc, key: assoc(
            acc, key, plainOrderToParamOrder(plainOrders[key]).value_or(None)
        ),
        plainOrders.keys(),
        {},
    )
