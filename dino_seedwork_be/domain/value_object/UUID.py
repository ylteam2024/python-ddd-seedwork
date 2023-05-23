from typing import Any, Union
from uuid import UUID as UUIDRaw

from returns.result import Result, Success, safe

from dino_seedwork_be.exceptions import IllegalArgumentException

from .AbstractIdentity import AbstractIdentity

# __all__ = ["UUID"]


class UUID(AbstractIdentity[UUIDRaw]):
    def __init__(self, an_id: Union[UUIDRaw, str]):
        match an_id:
            case UUIDRaw() as id:
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

    @safe
    def set_id(self, an_id: UUIDRaw | str):
        match an_id:
            case str(id):
                self._id = UUIDRaw(id)
            case UUIDRaw() as id:
                self._id = id

    def validate(self, an_id: UUIDRaw) -> Result[UUIDRaw, Any]:
        return Success(an_id)
