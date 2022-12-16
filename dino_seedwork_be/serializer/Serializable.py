from abc import ABC, abstractmethod
from typing import Generic, TypeVar


class JSONSerializable(ABC):
    @abstractmethod
    def as_dict(self) -> dict:
        pass

    def __getstate__(self):
        return self.as_dict()

    @staticmethod
    @abstractmethod
    def restore(a_dict: dict):
        ...

    def getValue(self):
        return self.__getstate__()
