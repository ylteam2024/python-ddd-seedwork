from typing import Generic, Type, TypeVar

from dino_seedwork_be.serializer.AbstractSerializer import AbstractSerializer
from dino_seedwork_be.serializer.Serializable import JSONSerializable

ObjectSerializable = TypeVar("ObjectSerializable", bound=JSONSerializable)
UnderlyingObject = TypeVar("UnderlyingObject")

__all__ = ["ObjectSerializer"]


class ObjectSerializer(AbstractSerializer, Generic[ObjectSerializable]):
    def __init__(self):
        super().__init__()

    def serialize(self, anObj: ObjectSerializable, toJson=False) -> str | object:
        if toJson:
            return str(self.json_marshaller().encode(anObj, unpicklable=False))
        return anObj.get_value()

    def deserialize(self, aJson, cls: Type[ObjectSerializable]):
        data = self.json_marshaller().decode(aJson)
        return cls.restore(data)
