from dataclasses import field

from returns.result import safe

from dino_seedwork_be.domain.assertion_concern import DomainAssertionConcern
from dino_seedwork_be.domain.value_objects import ID, UUID
from dino_seedwork_be.exceptions import IllegalArgumentException


class IdentifiedDomainObject(DomainAssertionConcern):
    id: ID = field(hash=True)

    def __eq__(self, obj):
        return self.id == obj.id

    def __init__(self):
        super().__init__()

    def getIdentity(self):
        return self.id

    def getRawId(self) -> str:
        return self.id.getRaw()

    @safe
    def setId(self, id: UUID | ID | str):
        match id:
            case UUID() as id:
                self.id = ID(id)
            case ID() as id:
                self.id = id
            case str() as id:
                self.id = ID(id)
            case _:
                raise IllegalArgumentException("id is not in correct type")
        return "OK"
