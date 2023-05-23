from dataclasses import field
from typing import Generic, TypeVar

from returns.maybe import Maybe, Nothing
from returns.result import safe

from dino_seedwork_be.domain.value_object.AbstractIdentity import \
    AbstractIdentity

from .DomainAssertionConcern import DomainAssertionConcern

# __all__ = ["IdentifiedDomainObject"]

IdentityType = TypeVar("IdentityType", bound=AbstractIdentity)


class IdentifiedDomainObject(Generic[IdentityType], DomainAssertionConcern):
    _id: Maybe[IdentityType]

    def __eq__(self, obj):
        return self._id == obj.id

    def __init__(self, id: Maybe[IdentityType] = Nothing):
        self.set_id(id)
        super().__init__()

    def identity(self) -> Maybe[IdentityType]:
        return self._id

    def id_as_string(self) -> Maybe[str]:
        return self._id.map(lambda id: id.get_raw_str())

    @safe
    def set_id(self, id: Maybe[IdentityType]):
        self._id = id
