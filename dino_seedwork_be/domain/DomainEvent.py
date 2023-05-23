import json
from datetime import datetime
from typing import Optional, TypedDict

from returns.functions import tap
from returns.maybe import Maybe, Some
from returns.pipeline import flow
from returns.pointfree import map_
from returns.result import Result, Success, safe
from toolz.dicttoolz import get_in

from dino_seedwork_be.logic.assertion_concern import AssertionConcern
from dino_seedwork_be.serializer.Serializable import JSONSerializable
from dino_seedwork_be.utils.date import now_utc, to_iso_format
from dino_seedwork_be.utils.functional import unwrap


class EmptyProps(TypedDict):
    pass


class DomainEvent(AssertionConcern, JSONSerializable):
    _id: int | None
    _version: int = 0
    _occurred_on: datetime
    _name: str
    _props: dict = {}

    def __init__(
        self,
        name: str,
        id: int | None = None,
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
                map_(lambda _: self.set_id(id)),
            )
        )

    def __eq__(self, __o: object) -> bool:
        match __o:
            case DomainEvent() as domain_event:
                return (
                    domain_event.name() == self.name()
                    and domain_event.props() == self.props()
                )
            case _:
                return False

    @staticmethod
    @safe
    def factory(
        occurred_on: datetime,
        name: str,
        version: int = 0,
        props: dict = {},
    ):
        return DomainEvent(name, None, version, occurred_on, props)

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

    def set_id(self, id: int | None) -> Result:
        self._id = id
        return Success(None)

    def set_name(self, a_name: str) -> Result:
        def set(_):
            self._name = a_name

        return flow(
            self.assert_argument_not_empty(Some(a_name)),
            map_(tap(set)),
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

    def body_json(self) -> str:
        return json.dumps(self.props(), default=str) or "{}"

    def props_to_dict(self):
        return self._props

    def as_dict(self):
        return {
            "version": self.version(),
            "occurred_on": to_iso_format(self.occurred_on()),
            "name": self.name(),
            "props": self.props_to_dict(),
            "id": self._id,
        }

    def id(self) -> Maybe[int]:
        return Maybe.from_optional(self._id)

    @staticmethod
    def restore(a_dict):
        return DomainEvent(
            version=get_in(["version"], a_dict, 0),
            occurred_on=Maybe.from_optional(get_in(["occurred_on"], a_dict, None))
            .map(str)
            .map(datetime.fromisoformat)
            .value_or(None),
            name=str(get_in(["name"], a_dict)),
            props=dict(get_in(["props"], a_dict, {})),
            id=int(get_in(["id"], a_dict)),
        )
