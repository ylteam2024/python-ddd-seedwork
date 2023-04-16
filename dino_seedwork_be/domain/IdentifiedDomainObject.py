from dataclasses import field
from typing import Generic, TypeVar

from returns.result import safe

from dino_seedwork_be.domain.value_object.AbstractIdentity import \
    AbstractIdentity

from .DomainAssertionConcern import DomainAssertionConcern

__all__ = ["IdentifiedDomainObject"]

IdentityType = TypeVar("IdentityType", bound=AbstractIdentity)


class IdentifiedDomainObject(Generic[IdentityType], DomainAssertionConcern):
    _id: IdentityType = field(hash=True)

    def __eq__(self, obj):
        return self._id == obj.id

    def __init__(self):
        super().__init__()

    def identity(self):
        return self._id

    def id_as_string(self) -> str:
        return self._id.get_raw_str()

    @safe
    def set_id(self, id: IdentityType):
        self._id = id
