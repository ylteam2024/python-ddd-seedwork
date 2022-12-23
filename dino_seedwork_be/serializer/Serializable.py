from abc import ABC, abstractmethod

__all__ = ["JSONSerializable"]


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

    def get_value(self):
        return self.__getstate__()
