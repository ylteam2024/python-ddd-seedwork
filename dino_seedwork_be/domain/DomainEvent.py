from datetime import datetime
from typing import Optional

from returns.functions import tap
from returns.maybe import Maybe
from returns.pipeline import flow
from returns.pointfree import map_
from returns.result import Result, Success, safe
from toolz.dicttoolz import get_in

from dino_seedwork_be.logic import AssertionConcern
from dino_seedwork_be.serializer import JSONSerializable
from dino_seedwork_be.utils import now_utc, set_protected_attr, unwrap

__all__ = ["DomainEvent"]


class DomainEvent(AssertionConcern, JSONSerializable):
    _version: int = 0
    _occurred_on: datetime
    _name: str
    _props: dict = {}

    def __init__(
        self,
        name: str,
        version: int = 0,
        occurred_on: Optional[datetime] = None,
        props: dict = {},
    ):
        unwrap(
            flow(
                None,
                lambda _: self.set_version(version),
                map_(lambda _: self.set_occurred_on(occurred_on or now_utc())),
                map_(lambda _: self.set_name(name)),
                map_(lambda _: self.set_props(props)),
            )
        )

    @staticmethod
    @safe
    def factory(
        occurred_on: datetime,
        name: str,
        version: int = 0,
        props: dict = {},
    ):
        return DomainEvent(name, version, occurred_on, props)

    def occurred_on(self) -> datetime:
        return self._occurred_on

    def version(self) -> int:
        return self._version

    def props(self) -> dict:
        return self._props

    def set_occurred_on(self, a_datetime: datetime) -> Result:
        self._occurred_on = a_datetime
        return Success(None)

    def set_version(self, a_version: int) -> Result:
        self._version = a_version
        return Success(None)

    def set_name(self, a_name: str) -> Result:
        return flow(
            self.assert_argument_not_empty(a_name),
            map_(tap(lambda _: set_protected_attr(self, "_name", a_name))),
        )

    def set_props(self, props: dict) -> Result:
        self._props = props
        return Success(None)

    def get_prop_attr(self, attr_name: str):
        return self._props[attr_name]

    def name(self) -> str:
        return self._name

    def type(self) -> str:
        return self.name()

    def as_dict(self):
        return {
            "version": self.version(),
            "occurred_on": self.occurred_on(),
            "name": self.name(),
            "props": self._props,
        }

    @staticmethod
    def restore(a_dict):
        return DomainEvent(
            version=get_in(["version"], a_dict, 0),
            occurred_on=Maybe.from_optional(get_in(["occurred_on"], a_dict, None))
            .map(str)
            .map(datetime.fromisoformat)
            .value_or(None),
            name=str(get_in(["name"], a_dict)),
            props=get_in(["props"], a_dict, {}),
        )
