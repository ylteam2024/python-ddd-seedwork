from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

from returns.result import Result

SerializableType = TypeVar("SerializableType")


class AbstractSerializer(ABC, Generic[SerializableType]):
    @abstractmethod
    def serialize(self, obj: SerializableType) -> Result[str, Any]:
        pass

    @abstractmethod
    def deserialize(self, an_json: str) -> Result[SerializableType, Any]:
        pass
