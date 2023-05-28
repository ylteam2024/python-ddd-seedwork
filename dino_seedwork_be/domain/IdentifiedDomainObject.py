from dataclasses import field
from typing import Generic, TypeVar

from returns.maybe import Maybe, Nothing
from returns.result import safe

from dino_seedwork_be.domain.value_object.AbstractIdentity import \
    AbstractIdentity
from dino_seedwork_be.utils.functional import get_class_name

from .DomainAssertionConcern import DomainAssertionConcern

# __all__ = ["IdentifiedDomainObject"]

IdentityType = TypeVar("IdentityType", bound=AbstractIdentity)


class IdentifiedDomainObject(Generic[IdentityType], DomainAssertionConcern):
    _id: Maybe[IdentityType]

    def __eq__(self, obj):
        return self._id == obj._id and get_class_name(self) == get_class_name(obj)

    def __init__(self, id: Maybe[IdentityType] = Nothing):
        self.set_id(id)
        super().__init__()

    def __hash__(self) -> int:
        return hash(
            (
                self.identity().map(lambda v: v.get_raw()).value_or(None),
                get_class_name(self),
            ),
        )

    def identity(self) -> Maybe[IdentityType]:
        return self._id

    def id_as_string(self) -> Maybe[str]:
        return self._id.map(lambda id: id.get_raw_str())

    @safe
    def set_id(self, id: Maybe[IdentityType]):
        self._id = id
