from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from returns.pipeline import flow
from returns.pointfree import map_
from sqlalchemy.engine import Result

from dino_seedwork_be.logic import AssertionConcern
from dino_seedwork_be.utils import get_class_name, set_protected_attr, unwrap

IdRawType = TypeVar("IdRawType")


class AbstractIdentity(ABC, AssertionConcern, Generic[IdRawType]):

    _id: IdRawType

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

    def __init__(self, id: IdRawType) -> None:
        super().__init__()
        unwrap(self.set_id(id))

    @abstractmethod
    def validate(self, an_id: IdRawType) -> Result:
        pass

    def set_id(self, an_id: IdRawType):
        return flow(
            self.assert_argument_not_null(an_id),
            map_(self.validate),
            map_(lambda _: set_protected_attr(self, "_id", an_id)),
        )
