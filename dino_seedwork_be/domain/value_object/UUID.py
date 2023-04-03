from typing import Union
from uuid import UUID as UUIDRaw

from dino_seedwork_be.exceptions import IllegalArgumentException

from .AbstractIdentity import AbstractIdentity


class UUID(AbstractIdentity[UUIDRaw]):
    def __init__(self, an_id: Union[UUIDRaw, str]):
        match an_id:
            case UUIDRaw(id):
                super().__init__(id)
            case str(id):
                super().__init__(UUIDRaw(id))
            case _:
                raise IllegalArgumentException("id should be UUID or UUID string")

    def __eq__(self, obj):
        match obj:
            case UUID():
                return self.id() == obj.id()
            case _:
                return False

    def __hash__(self) -> int:
        return hash(self.get_raw())

    def set_id(self, an_id: UUIDRaw | str):
        match an_id:
            case str(id):
                self._id = UUIDRaw(id)
            case UUIDRaw(id):
                self._id = id
