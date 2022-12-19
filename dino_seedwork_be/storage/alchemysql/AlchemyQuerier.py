from functools import reduce
from typing import Any, List, Optional

from sqlalchemy import TEXT, Column, and_, cast, func, or_
from sqlalchemy.ext.asyncio.session import AsyncSession

from dino_seedwork_be.adapters.rest import (FilterElement, OrderParam,
                                            ParamOperators, ParamWithComparing)
from dino_seedwork_be.application.query import BaseQuerier
from dino_seedwork_be.exceptions import MainException
from dino_seedwork_be.storage.uow import DBSessionUser
from dino_seedwork_be.utils.list import remove_none


class AlchemyQuerier(BaseQuerier):
    _query_session: AsyncSession

    def set_session(self, session: AsyncSession):
        self._query_session = session

    def apply_session(self, sessionUsers: List[DBSessionUser]):
        for user in sessionUsers:
            user.set_session(self.session())

    def session(self) -> AsyncSession:
        return self._query_session

    def is_allowed_primitive(self, v: Any):
        return (
            isinstance(v, bool)
            or isinstance(v, str)
            or isinstance(v, int)
            or isinstance(v, float)
        )

    def a_param_to_colum_filter(
        self, param: Any | ParamWithComparing, column: Column, is_collection: bool
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
            case p if self.is_allowed_primitive(p):
                match is_collection:
                    case False:
                        return column == param
                    case True:
                        return column.any(param)
            case _:
                return None

    def param_list_to_column_filter(
        self,
        param: List[Any] | List[ParamWithComparing],
        column: Column,
        is_collection: bool,
    ):
        match param:
            case [*elems] if all(isinstance(e, ParamWithComparing) for e in elems):
                return and_(
                    *[
                        self.a_param_to_colum_filter(p, column, is_collection)
                        for p in param
                    ]
                )
            case [*elems] if all(self.is_allowed_primitive(e) for e in elems):
                return or_(
                    *[
                        self.a_param_to_colum_filter(p, column, is_collection)
                        for p in param
                    ]
                )
            case _:
                return None

    def param_to_column_filter(
        self, param: FilterElement, column: Column, is_collection: bool = False
    ):
        match param:
            case list():
                return remove_none(
                    [self.param_list_to_column_filter(param, column, is_collection)]
                )
            case _:
                return remove_none(
                    [self.a_param_to_colum_filter(param, column, is_collection)]
                )

    @staticmethod
    def gen_space_interwine_columns(columns: List[Column]):
        def reduce_interwine_with_space(acc, value):
            match value[0]:
                case int() as index if index == len(columns) - 1:
                    return [*acc, value[1]]
                case _:
                    return [*acc, value[1], " "]

        return func.concat(*reduce(reduce_interwine_with_space, enumerate(columns), []))

    def fuzzy_search(self, columns: List[Column], q: Optional[str] = None):
        distance_score = (
            AlchemyQuerier.gen_space_interwine_columns(columns)
            .op("<->")(cast(q, TEXT))
            .label("distance_score")
        )
        match q:
            case str(text) if text.strip() != "":
                return {
                    "select": [distance_score],
                    "filter": [distance_score < 0.95],
                    "order": [distance_score],
                }
            case _:
                return {"select": [], "filter": [], "order": []}

    def get_order_query(self, column: Column, order: Optional[OrderParam]):
        match order:
            case OrderParam.ASC:
                return [column.asc()]
            case OrderParam.DESC:
                return [column.desc()]
            case None:
                return []

    def get_order_query_list(self, orders: List[tuple[Column, OrderParam]]):
        def order_to_db_query(order: tuple[Column, OrderParam]):
            match order[1]:
                case OrderParam.ASC:
                    return order[0].asc()
                case OrderParam.DESC:
                    return order[0].desc()

        return map(order_to_db_query, orders)
