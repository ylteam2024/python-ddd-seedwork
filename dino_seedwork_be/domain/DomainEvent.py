import json
from datetime import datetime
from typing import Generic, Optional, TypedDict, TypeVar, cast

from returns.functions import tap
from returns.maybe import Maybe, Nothing
from returns.pipeline import flow
from returns.pointfree import map_
from returns.result import Result, Success, safe
from toolz.dicttoolz import get_in

from dino_seedwork_be.logic.assertion_concern import AssertionConcern
from dino_seedwork_be.serializer.Serializable import JSONSerializable
from dino_seedwork_be.utils.date import now_utc, to_iso_format
from dino_seedwork_be.utils.functional import set_protected_attr, unwrap


class EmptyProps(TypedDict):
    pass


DomainEventProps = TypeVar("DomainEventProps", bound=TypedDict, default=EmptyProps)


class DomainEvent(Generic[DomainEventProps], AssertionConcern, JSONSerializable):
    _id: Maybe[int]
    _version: int = 0
    _occurred_on: datetime
    _name: str
    _props: DomainEventProps

    def __init__(
        self,
        name: str,
        id: Maybe[int],
        props: DomainEventProps,
        version: int = 0,
        occurred_on: Optional[datetime] = None,
    ):
        unwrap(
            flow(
                None,
                lambda _: self.set_version(version),
                map_(lambda _: self.set_occurred_on(occurred_on or now_utc())),
                map_(lambda _: self.set_name(name)),
                map_(lambda _: self.set_props(props)),
                map_(lambda _: self.set_id(id.unwrap())),
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
        props: DomainEventProps,
        version: int = 0,
    ):
        return DomainEvent(name, Nothing, props, version, occurred_on)

    def occurred_on(self) -> datetime:
        return self._occurred_on

    def version(self) -> int:
        return self._version

    def props(self) -> DomainEventProps:
        return self._props

    def set_occurred_on(self, a_datetime: datetime) -> Result:
        self._occurred_on = a_datetime
        return Success(None)

    def set_version(self, a_version: int) -> Result:
        self._version = a_version
        return Success(None)

    def set_id(self, id: int | None) -> Result:
        self._id = Maybe.from_optional(id)
        return Success(None)

    def set_name(self, a_name: str) -> Result:
        return flow(
            self.assert_argument_not_empty(a_name),
            map_(tap(lambda _: set_protected_attr(self, "_name", a_name))),
        )

    def set_props(self, props: DomainEventProps) -> Result:
        self._props = props
        return Success(None)

    def get_prop_attr(self, attr_name: str):
        return getattr(self._props, attr_name)

    def name(self) -> str:
        return self._name

    def type(self) -> str:
        return self.name()

    def body_json(self) -> str:
        return json.dumps(self.props())

    def as_dict(self):
        return {
            "version": self.version(),
            "occurred_on": to_iso_format(self.occurred_on()),
            "name": self.name(),
            "props": self._props,
            "id": self._id,
        }

    def id(self) -> Maybe[int]:
        return self._id

    @classmethod
    def restore(cls, a_dict):
        return DomainEvent(
            version=cast(int, get_in(["version"], a_dict, 0)),
            occurred_on=Maybe.from_optional(get_in(["occurred_on"], a_dict, None))
            .map(str)
            .map(datetime.fromisoformat)
            .value_or(None),
            name=str(get_in(["name"], a_dict)),
            props=a_dict,
            id=Maybe.from_optional(cast(int, get_in(["id"], a_dict))),
        )
