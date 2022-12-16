from functools import reduce
from typing import Any, List, Optional

from sqlalchemy import (CHAR, TEXT, VARCHAR, Column, Integer, Text, and_, cast,
                        func, or_)
from sqlalchemy.ext.asyncio.session import AsyncSession

from src.seedwork.adapters.rest import (FilterElement, FilterSet, OrderParam,
                                        ParamOperators, ParamWithComparing)
from src.seedwork.application.query import BaseQuerier
from src.seedwork.exceptions import MainException
from src.seedwork.storage.uow import DBSessionUser
from src.seedwork.utils.list import removeNone


class AlchemyQuerier(BaseQuerier):
    __querySession: AsyncSession

    def setSession(self, session: AsyncSession):
        self.__querySession = session

    def applySession(self, sessionUsers: List[DBSessionUser]):
        for user in sessionUsers:
            user.setSession(self.getSession())

    def getSession(self) -> AsyncSession:
        return self.__querySession

    def session(self) -> AsyncSession:
        return self.__querySession

    def isAllowedPrimitive(self, v: Any):
        return (
            isinstance(v, bool)
            or isinstance(v, str)
            or isinstance(v, int)
            or isinstance(v, float)
        )

    def aParamToColumFilter(
        self, param: Any | ParamWithComparing, column: Column, isCollection: bool
    ):
        match param:
            case ParamWithComparing():
                match param.operator:
                    case ParamOperators.LT:
                        return column < param.value
                    case ParamOperators.LTE:
                        return column <= param.value
                    case ParamOperators.GT:
                        return column > param.value
                    case ParamOperators.GTE:
                        return column >= param.value
                    case ParamOperators.EQ:
                        return column == param.value
                    case _:
                        raise MainException(code="UNKNOWN_PARAM_COMPARATOR")
            case p if self.isAllowedPrimitive(p):
                match isCollection:
                    case False:
                        return column == param
                    case True:
                        return column.any(param)
            case _:
                return None

    def paramListToColumnFilter(
        self,
        param: List[Any] | List[ParamWithComparing],
        column: Column,
        isCollection: bool,
    ):
        match param:
            case [*elems] if all(isinstance(e, ParamWithComparing) for e in elems):
                return and_(
                    *[self.aParamToColumFilter(p, column, isCollection) for p in param]
                )
            case [*elems] if all(self.isAllowedPrimitive(e) for e in elems):
                return or_(
                    *[self.aParamToColumFilter(p, column, isCollection) for p in param]
                )
            case _:
                return None

    def paramToColumnFilter(
        self, param: FilterElement, column: Column, isCollection: bool = False
    ):
        match param:
            case list():
                return removeNone(
                    [self.paramListToColumnFilter(param, column, isCollection)]
                )
            case _:
                return removeNone(
                    [self.aParamToColumFilter(param, column, isCollection)]
                )

    @staticmethod
    def genSpaceInterwineColumns(columns: List[Column]):
        def reduceInterwineWithSpace(acc, value):
            match value[0]:
                case int() as index if index == len(columns) - 1:
                    return [*acc, value[1]]
                case _:
                    return [*acc, value[1], " "]

        return func.concat(*reduce(reduceInterwineWithSpace, enumerate(columns), []))

    def fuzzySearch(self, columns: List[Column], q: Optional[str] = None):
        distanceScore = (
            AlchemyQuerier.genSpaceInterwineColumns(columns)
            .op("<->")(cast(q, TEXT))
            .label("distance_score")
        )
        match q:
            case str(text) if text.strip() != "":
                return {
                    "select": [distanceScore],
                    "filter": [distanceScore < 0.95],
                    "order": [distanceScore],
                }
            case _:
                return {"select": [], "filter": [], "order": []}

    def getOrderQuery(self, column: Column, order: Optional[OrderParam]):
        match order:
            case OrderParam.ASC:
                return [column.asc()]
            case OrderParam.DESC:
                return [column.desc()]
            case None:
                return []

    def getOrderQueryList(self, orders: List[tuple[Column, OrderParam]]):
        def orderToDbQuery(order: tuple[Column, OrderParam]):
            match order[1]:
                case OrderParam.ASC:
                    return order[0].asc()
                case OrderParam.DESC:
                    return order[0].desc()

        return map(orderToDbQuery, orders)
