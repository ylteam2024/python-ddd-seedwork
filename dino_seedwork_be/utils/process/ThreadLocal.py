import threading
from typing import Generic, TypeVar

InnerValue = TypeVar("InnerValue")


class ThreadLocal(Generic[InnerValue]):
    _storage: threading.local
    _key: str

    def __init__(self, key: str, initValue: InnerValue):
        self._storage = threading.local()
        self._key = key
        setattr(self._storage, key, initValue)

    def value(self) -> InnerValue:
        return getattr(self._storage, self._key)

    def set_value(self, aValue: InnerValue):
        setattr(self._storage, self._key, aValue)
