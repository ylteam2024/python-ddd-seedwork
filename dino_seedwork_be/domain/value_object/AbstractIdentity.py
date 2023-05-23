from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

from returns.functions import tap
from returns.pipeline import flow
from returns.pointfree import bind, map_
from returns.result import Result

from dino_seedwork_be.utils import get_class_name, set_protected_attr, unwrap

from .AbstractValueObject import ValueObject

IdRawType = TypeVar("IdRawType")

# __all__ = ["AbstractIdentity"]


class AbstractIdentity(ABC, ValueObject, Generic[IdRawType]):

    _id: IdRawType

    def __init__(self, id: IdRawType) -> None:
        super().__init__()
        unwrap(self.set_id(id))

    def id(self) -> IdRawType:
        return self._id

    def __eq__(self, __o: object) -> bool:
        match __o:
            case AbstractIdentity():
                return type(__o) == type(self) and self.id() == __o.id()
            case _:
                return False

    def __str__(self) -> str:
        return f"{get_class_name(self)} [id={str(id)}]"

    def __hash__(self) -> int:
        return hash(self.get_raw())

    @abstractmethod
    def validate(self, an_id: IdRawType) -> Result[IdRawType, Any]:
        pass

    def set_id(self, an_id: IdRawType):
        def set(an_id):
            self._id = an_id

        return flow(
            an_id,
            self.assert_argument_not_null,
            bind(self.validate),
            map_(tap(set)),
        )

    def get_raw(self) -> IdRawType:
        return self.id()

    def get_raw_str(self) -> str:
        return str(self.id())

    def __getstate__(self):
        return self.__str__()
