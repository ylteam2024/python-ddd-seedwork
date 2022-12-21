from dataclasses import field

from returns.result import safe

from dino_seedwork_be.domain.value_objects import ID, UUID
from dino_seedwork_be.exceptions import IllegalArgumentException
from dino_seedwork_be.logic import DomainAssertionConcern


class IdentifiedDomainObject(DomainAssertionConcern):
    _id: ID = field(hash=True)

    def __eq__(self, obj):
        return self._id == obj.id

    def __init__(self):
        super().__init__()

    def identity(self):
        return self._id

    def raw_id(self) -> str:
        return self._id.get_raw()

    @safe
    def setId(self, id: UUID | ID | str):
        match id:
            case UUID() as id:
                self._id = ID(id)
            case ID() as id:
                self._id = id
            case str() as id:
                self._id = ID(id)
            case _:
                raise IllegalArgumentException("id is not in correct type")
        return "OK"
